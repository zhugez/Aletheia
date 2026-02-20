from __future__ import annotations

import hashlib
import json
import math
import os
from typing import Any
from urllib import request


class QdrantAdapter:
    def __init__(self, base_url: str | None = None, collection: str | None = None, vector_size: int = 64, timeout: int = 5):
        self.base_url = (base_url or os.getenv("QDRANT_URL", "http://localhost:6333")).rstrip("/")
        self.collection = collection or os.getenv("QDRANT_COLLECTION", "aletheia_chunks")
        self.vector_size = vector_size
        self.timeout = timeout

    def _http(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        data = json.dumps(body).encode("utf-8") if body is not None else None
        req = request.Request(
            f"{self.base_url}{path}",
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with request.urlopen(req, timeout=self.timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def _embed(self, text: str) -> list[float]:
        # Minimal deterministic embedding to avoid external model dependency in MVP.
        vec = [0.0] * self.vector_size
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            idx = int.from_bytes(digest[:2], "big") % self.vector_size
            sign = -1.0 if digest[2] % 2 else 1.0
            vec[idx] += sign * (1.0 + (digest[3] / 255.0))
        norm = math.sqrt(sum(v * v for v in vec)) or 1.0
        return [v / norm for v in vec]

    def ensure_collection(self) -> None:
        body = {
            "vectors": {
                "size": self.vector_size,
                "distance": "Cosine",
            }
        }
        try:
            self._http("PUT", f"/collections/{self.collection}", body)
        except Exception:
            # Existing collection or transient issue.
            pass

    def index_chunks(self, chunks: list[dict[str, Any]]) -> int:
        if not chunks:
            return 0
        self.ensure_collection()
        points = []
        for i, chunk in enumerate(chunks):
            chunk_id = chunk.get("chunk_id") or f"chunk-{i}"
            points.append(
                {
                    "id": chunk_id,
                    "vector": self._embed(chunk.get("text_content", "")),
                    "payload": {
                        "chunk_id": chunk_id,
                        "source_id": chunk.get("source_id"),
                        "title": chunk.get("title"),
                        "chapter": chunk.get("chapter"),
                        "page_start": chunk.get("page_start"),
                        "page_end": chunk.get("page_end"),
                        "text_content": chunk.get("text_content", ""),
                    },
                }
            )
        # Upsert is idempotent and avoids conflict errors on re-ingest.
        self._http("PUT", f"/collections/{self.collection}/points?wait=true", {"points": points})
        return len(points)

    def query(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        body = {
            "vector": self._embed(query),
            "limit": top_k,
            "with_payload": True,
        }
        res = self._http("POST", f"/collections/{self.collection}/points/search", body)
        out: list[dict[str, Any]] = []
        for row in res.get("result", []):
            payload = row.get("payload") or {}
            out.append(
                {
                    "chunk_id": payload.get("chunk_id"),
                    "source_id": payload.get("source_id"),
                    "title": payload.get("title"),
                    "chapter": payload.get("chapter"),
                    "page_start": payload.get("page_start"),
                    "page_end": payload.get("page_end"),
                    "text": payload.get("text_content", ""),
                    "score": float(row.get("score") or 0.0),
                    "retrieval": "vector",
                }
            )
        return out
