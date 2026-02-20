from __future__ import annotations

from typing import Any

try:
    from ..adapters.opensearch_adapter import OpenSearchAdapter
    from ..adapters.qdrant_adapter import QdrantAdapter
except Exception:
    from adapters.opensearch_adapter import OpenSearchAdapter
    from adapters.qdrant_adapter import QdrantAdapter


def _normalize_score(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return items
    max_score = max((float(i.get("score") or 0.0) for i in items), default=1.0) or 1.0
    for item in items:
        item["norm_score"] = float(item.get("score") or 0.0) / max_score
    return items


def hybrid_search(query: str, top_k: int, domain: str | None = None) -> list[dict[str, Any]]:
    results_by_chunk: dict[str, dict[str, Any]] = {}

    bm25: list[dict[str, Any]] = []
    vector: list[dict[str, Any]] = []

    try:
        bm25 = OpenSearchAdapter().query(query=query, top_k=top_k, domain=domain)
    except Exception:
        bm25 = []

    try:
        vector = QdrantAdapter().query(query=query, top_k=top_k)
    except Exception:
        vector = []

    _normalize_score(bm25)
    _normalize_score(vector)

    for item in bm25 + vector:
        chunk_id = item.get("chunk_id") or f"fallback-{len(results_by_chunk)}"
        if chunk_id not in results_by_chunk:
            results_by_chunk[chunk_id] = {
                **item,
                "hybrid_score": float(item.get("norm_score") or 0.0),
            }
            continue
        results_by_chunk[chunk_id]["hybrid_score"] += float(item.get("norm_score") or 0.0)

    merged = sorted(results_by_chunk.values(), key=lambda x: x.get("hybrid_score", 0.0), reverse=True)
    return [
        {
            "text": row.get("text", ""),
            "source_id": row.get("source_id"),
            "title": row.get("title"),
            "chapter": row.get("chapter"),
            "page_start": row.get("page_start"),
            "page_end": row.get("page_end"),
            "score": round(float(row.get("hybrid_score") or 0.0), 4),
            "chunk_id": row.get("chunk_id"),
        }
        for row in merged[:top_k]
    ]


def synthesize_grounded_answer(question: str, citations: list[dict[str, Any]]) -> tuple[str, str, bool]:
    if not citations:
        return ("I could not find grounded evidence for this question in the indexed corpus.", "low", True)

    snippets = [c.get("text", "").strip() for c in citations if c.get("text")]
    snippets = [s for s in snippets if s]
    if not snippets:
        return ("I found candidate citations, but they did not contain usable text.", "low", True)

    top = snippets[:3]
    answer = " ".join(top)
    # Keep answer concise and grounded in retrieved text.
    answer = answer[:900].strip()

    confidence = "high" if len(citations) >= 3 else "medium"
    return (answer, confidence, False)
