from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import PurePosixPath
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

try:
    from .services.cache_store import CacheStore
    from .services.job_queue import enqueue_ingest, get_job_status, retry_job, cancel_job
    from .services.retrieval import hybrid_search, synthesize_grounded_answer
except Exception:
    try:
        from services.cache_store import CacheStore
        from services.job_queue import enqueue_ingest, get_job_status, retry_job, cancel_job
        from services.retrieval import hybrid_search, synthesize_grounded_answer
    except Exception:
        def hybrid_search(query: str, top_k: int, domain: str | None = None) -> list[dict[str, Any]]:
            return []

        def synthesize_grounded_answer(question: str, citations: list[dict[str, Any]]) -> tuple[str, str, bool]:
            return (
                "I could not find grounded evidence for this question in the indexed corpus.",
                "low",
                True,
            )

        def enqueue_ingest(source_uri: str, source_type: str = "book", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
            return {"job_id": None, "status": "queue_unavailable", "source_uri": source_uri, "source_type": source_type}

        def get_job_status(job_id: str) -> dict[str, Any]:
            return {"job_id": job_id, "status": "queue_unavailable"}
            
        def retry_job(job_id: str) -> dict[str, Any]:
            return {"job_id": job_id, "status": "queue_unavailable"}

        def cancel_job(job_id: str) -> dict[str, Any]:
            return {"job_id": job_id, "status": "queue_unavailable"}

        class CacheStore:  # type: ignore
            def make_key(self, namespace: str, payload: dict[str, Any]) -> str:
                return f"{namespace}:{payload}"

            def get(self, key: str) -> dict[str, Any] | None:
                return None

            def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
                return None

            def is_ready(self) -> bool:
                return True

            def clear_namespace(self, namespace: str) -> int:
                return 0

            def clear_all(self) -> int:
                return 0


ALLOWED_UPLOAD_EXTENSIONS = {
    ".pdf", ".epub",
    ".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff",
}

app = FastAPI(title="Aletheia API", version="0.3.0")

_cors_origins = [
    o.strip()
    for o in os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost:8081,http://localhost:4321").split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
cache = CacheStore()
SEARCH_CACHE_TTL = int(os.getenv("SEARCH_CACHE_TTL", "300"))
ASK_CACHE_TTL = int(os.getenv("ASK_CACHE_TTL", "180"))


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    domain: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: str = Field(default="grounded")


class IngestRequest(BaseModel):
    source_uri: str = Field(..., min_length=1)
    source_type: str = Field(default="book")
    metadata: dict[str, Any] = Field(default_factory=dict)


class CacheClearRequest(BaseModel):
    namespace: str = Field(default="all")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "aletheia-api",
        "cache_ready": cache.is_ready(),
    }


@app.post("/search")
def search(req: SearchRequest) -> dict[str, Any]:
    key = cache.make_key("search", req.model_dump())
    cached = cache.get(key)
    if cached is not None:
        return {"request_id": str(uuid4()), **cached, "cache": "hit"}

    results = hybrid_search(query=req.query, top_k=req.top_k, domain=req.domain)
    payload = {
        "query": req.query,
        "domain": req.domain,
        "results": results,
    }
    cache.set(key, payload, SEARCH_CACHE_TTL)
    return {"request_id": str(uuid4()), **payload, "cache": "miss"}


@app.post("/ask")
def ask(req: AskRequest) -> dict[str, Any]:
    key = cache.make_key("ask", req.model_dump())
    cached = cache.get(key)
    if cached is not None:
        return {"request_id": str(uuid4()), **cached, "cache": "hit"}

    citations = hybrid_search(query=req.question, top_k=req.top_k)
    answer, confidence, insufficient = synthesize_grounded_answer(req.question, citations)
    payload = {
        "question": req.question,
        "mode": req.mode,
        "answer": answer,
        "confidence": confidence,
        "insufficient_evidence": insufficient,
        "citations": citations,
    }
    cache.set(key, payload, ASK_CACHE_TTL)
    return {"request_id": str(uuid4()), **payload, "cache": "miss"}


@app.post("/ingest")
def ingest(req: IngestRequest) -> dict[str, Any]:
    return enqueue_ingest(req.source_uri, req.source_type, req.metadata)


@app.get("/jobs/{job_id}")
def job_status(job_id: str) -> dict[str, Any]:
    return get_job_status(job_id)

@app.post("/jobs/{job_id}/retry")
def retry_job_endpoint(job_id: str) -> dict[str, Any]:
    return retry_job(job_id)

@app.post("/jobs/{job_id}/cancel")
def cancel_job_endpoint(job_id: str) -> dict[str, Any]:
    return cancel_job(job_id)


@app.post("/cache/clear")
def clear_cache(req: CacheClearRequest) -> dict[str, Any]:
    namespace = (req.namespace or "all").strip().lower()
    if namespace in ("all", "*"):
        deleted = cache.clear_all()
        return {"status": "ok", "namespace": "all", "deleted": deleted}
    if namespace not in ("search", "ask"):
        return {"status": "error", "message": "namespace must be one of: all, search, ask"}
    deleted = cache.clear_namespace(namespace)
    return {"status": "ok", "namespace": namespace, "deleted": deleted}


@app.post("/upload")
async def upload_document(file: UploadFile = File(...), source_type: str = "document"):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    ext = PurePosixPath(file.filename).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}",
        )

    # Save file to a temporary location
    temp_dir = tempfile.gettempdir()
    safe_name = PurePosixPath(file.filename).name
    file_path = os.path.join(temp_dir, f"{uuid4().hex}_{safe_name}")
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save file")

    # Send it to the ingest queue (passing the local URI)
    local_uri = f"file://{file_path}"
    
    metadata = {
        "original_filename": file.filename,
        "content_type": file.content_type,
    }
    
    result = enqueue_ingest(local_uri, source_type, metadata)
    return {"status": "ok", "message": "File uploaded successfully", "job": result}


@app.post("/upload/batch")
async def upload_batch(
    files: list[UploadFile] = File(...),
    metadata: str = Form("{}")
):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
        
    try:
        meta_dict = json.loads(metadata)
    except Exception:
        meta_dict = {}

    batch_id = f"b-{str(uuid4())[:8]}"
    jobs = []
    
    temp_dir = tempfile.gettempdir()
    
    for file in files:
        if not file.filename:
            continue

        ext = PurePosixPath(file.filename).suffix.lower()
        if ext not in ALLOWED_UPLOAD_EXTENSIONS:
            jobs.append({
                "job_id": None,
                "filename": file.filename,
                "status": "rejected",
                "error": f"Unsupported file type '{ext}'",
            })
            continue

        file_path = os.path.join(temp_dir, f"{uuid4().hex}_{PurePosixPath(file.filename).name}")
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
                
            local_uri = f"file://{file_path}"
            file_meta = {
                "original_filename": file.filename,
                "content_type": file.content_type,
                "batch_id": batch_id,
                **meta_dict
            }
            # Enqueue the job
            result = enqueue_ingest(local_uri, "document", file_meta)
            jobs.append({
                "job_id": result.get("job_id"),
                "filename": file.filename,
                "status": result.get("status", "queued")
            })
        except Exception:
            jobs.append({
                "job_id": None,
                "filename": file.filename,
                "status": "failed",
                "error": "failed to save file"
            })

    cache.set(f"batch:{batch_id}", {"batch_id": batch_id, "jobs": jobs}, 86400)
    return {"batch_id": batch_id, "jobs": jobs}


@app.get("/upload/batch/{batch_id}")
async def get_batch_status(batch_id: str) -> dict[str, Any]:
    batch_data = cache.get(f"batch:{batch_id}")
    if not batch_data:
        raise HTTPException(status_code=404, detail="Batch not found")

    updated_jobs = []
    for job in batch_data.get("jobs", []):
        if job.get("job_id"):
            job.update(get_job_status(job["job_id"]))
        updated_jobs.append(job)

    total = len(updated_jobs)
    done = sum(1 for j in updated_jobs if j.get("status") == "finished")
    failed = sum(1 for j in updated_jobs if j.get("status") in ("failed", "canceled"))

    batch_data["jobs"] = updated_jobs
    batch_data["summary"] = {
        "total": total,
        "done": done,
        "failed": failed,
        "in_progress": total - done - failed,
    }
    return batch_data
