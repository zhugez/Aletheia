from __future__ import annotations

import os
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from .services.cache_store import CacheStore
    from .services.job_queue import enqueue_ingest, get_job_status
    from .services.retrieval import hybrid_search, synthesize_grounded_answer
except Exception:
    try:
        from services.cache_store import CacheStore
        from services.job_queue import enqueue_ingest, get_job_status
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

        class CacheStore:  # type: ignore
            def make_key(self, namespace: str, payload: dict[str, Any]) -> str:
                return f"{namespace}:{payload}"

            def get(self, key: str) -> dict[str, Any] | None:
                return None

            def set(self, key: str, value: dict[str, Any], ttl_seconds: int) -> None:
                return None

            def is_ready(self) -> bool:
                return True


app = FastAPI(title="Aletheia API", version="0.3.0")
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
