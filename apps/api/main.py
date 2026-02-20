from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

try:
    from .services.retrieval import hybrid_search, synthesize_grounded_answer
except Exception:
    try:
        from services.retrieval import hybrid_search, synthesize_grounded_answer
    except Exception:
        # Graceful fallback if retrieval service wiring is unavailable.
        def hybrid_search(query: str, top_k: int, domain: str | None = None) -> list[dict[str, Any]]:
            return []

        def synthesize_grounded_answer(question: str, citations: list[dict[str, Any]]) -> tuple[str, str, bool]:
            return (
                "I could not find grounded evidence for this question in the indexed corpus.",
                "low",
                True,
            )

app = FastAPI(title="Aletheia API", version="0.2.0")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    domain: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: str = Field(default="grounded")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aletheia-api"}


@app.post("/search")
def search(req: SearchRequest) -> dict[str, Any]:
    results = hybrid_search(query=req.query, top_k=req.top_k, domain=req.domain)
    return {
        "request_id": str(uuid4()),
        "query": req.query,
        "domain": req.domain,
        "results": results,
    }


@app.post("/ask")
def ask(req: AskRequest) -> dict[str, Any]:
    citations = hybrid_search(query=req.question, top_k=req.top_k)
    answer, confidence, insufficient = synthesize_grounded_answer(req.question, citations)

    return {
        "request_id": str(uuid4()),
        "question": req.question,
        "mode": req.mode,
        "answer": answer,
        "confidence": confidence,
        "insufficient_evidence": insufficient,
        "citations": citations,
    }
