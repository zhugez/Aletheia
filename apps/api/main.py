from __future__ import annotations

from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Aletheia API", version="0.2.0")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    domain: str | None = None


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    mode: str = Field(default="grounded")


def _placeholder_results(query: str, top_k: int) -> list[dict[str, Any]]:
    results = [
        {
            "text": f"Placeholder evidence for query: {query}",
            "source_id": "demo-source-001",
            "title": "Demo Book",
            "author": "Aletheia Team",
            "chapter": "1",
            "page_start": 1,
            "page_end": 2,
            "score": 0.82,
        },
        {
            "text": "Second evidence snippet for grounding.",
            "source_id": "demo-source-002",
            "title": "Research Notes",
            "author": "Aletheia Team",
            "chapter": "2",
            "page_start": 10,
            "page_end": 11,
            "score": 0.71,
        },
    ]
    return results[:top_k]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "aletheia-api"}


@app.post("/search")
def search(req: SearchRequest) -> dict[str, Any]:
    return {
        "request_id": str(uuid4()),
        "query": req.query,
        "domain": req.domain,
        "results": _placeholder_results(req.query, req.top_k),
    }


@app.post("/ask")
def ask(req: AskRequest) -> dict[str, Any]:
    citations = _placeholder_results(req.question, req.top_k)
    insufficient = len(citations) == 0

    if insufficient:
        answer = "Insufficient evidence found in the current knowledge base."
        confidence = "low"
    else:
        answer = (
            "Based on available sources, this is a placeholder grounded answer. "
            "Replace with synthesis from hybrid retrieval + reranker in next step."
        )
        confidence = "medium"

    return {
        "request_id": str(uuid4()),
        "question": req.question,
        "mode": req.mode,
        "answer": answer,
        "confidence": confidence,
        "insufficient_evidence": insufficient,
        "citations": citations,
    }
