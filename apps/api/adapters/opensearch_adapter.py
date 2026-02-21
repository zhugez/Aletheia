from __future__ import annotations

import json
import os
from typing import Any
from urllib import error, request


class OpenSearchAdapter:
    def __init__(self, base_url: str | None = None, index_name: str | None = None, timeout: int = 5):
        self.base_url = (base_url or os.getenv("OPENSEARCH_URL", "http://localhost:9200")).rstrip("/")
        self.index_name = index_name or os.getenv("OPENSEARCH_INDEX", "aletheia_chunks")
        self.timeout = timeout

    def _http(self, method: str, path: str, body: dict[str, Any] | str | None = None) -> dict[str, Any]:
        data: bytes | None = None
        headers = {"Content-Type": "application/json"}
        if body is not None:
            if isinstance(body, str):
                data = body.encode("utf-8")
                headers = {"Content-Type": "application/x-ndjson"}
            else:
                data = json.dumps(body).encode("utf-8")

        req = request.Request(f"{self.base_url}{path}", data=data, method=method, headers=headers)
        with request.urlopen(req, timeout=self.timeout) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}

    def ensure_index(self) -> None:
        mapping = {
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "source_id": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "chapter": {"type": "keyword"},
                    "page_start": {"type": "integer"},
                    "page_end": {"type": "integer"},
                    "text_content": {"type": "text"},
                }
            }
        }
        try:
            self._http("PUT", f"/{self.index_name}", mapping)
        except error.HTTPError as e:
            if e.code != 400:
                raise

    def index_chunks(self, chunks: list[dict[str, Any]]) -> int:
        if not chunks:
            return 0
        self.ensure_index()
        lines: list[str] = []
        for chunk in chunks:
            lines.append(json.dumps({"index": {"_index": self.index_name, "_id": chunk["chunk_id"]}}))
            lines.append(json.dumps(chunk))
        payload = "\n".join(lines) + "\n"
        res = self._http("POST", "/_bulk", payload)
        if res.get("errors"):
            raise RuntimeError("OpenSearch bulk indexing reported errors")
        return len(chunks)

    def query(self, query: str, top_k: int = 5, domain: str | None = None) -> list[dict[str, Any]]:
        if not query.strip():
            return []

        body: dict[str, Any] = {
            "size": top_k,
            "query": {
                "bool": {
                    "must": [
                        {
                            "simple_query_string": {
                                "query": query,
                                "fields": ["text_content^3", "title^2", "chapter"],
                                "default_operator": "or",
                            }
                        }
                    ]
                }
            },
        }
        if domain:
            body["query"]["bool"]["filter"] = [{"term": {"domain.keyword": domain}}]

        res = self._http("POST", f"/{self.index_name}/_search", body)
        out: list[dict[str, Any]] = []
        for hit in res.get("hits", {}).get("hits", []):
            src = hit.get("_source", {})
            out.append(
                {
                    "chunk_id": src.get("chunk_id"),
                    "source_id": src.get("source_id"),
                    "title": src.get("title"),
                    "chapter": src.get("chapter"),
                    "page_start": src.get("page_start"),
                    "page_end": src.get("page_end"),
                    "text": src.get("text_content", ""),
                    "score": float(hit.get("_score") or 0.0),
                    "retrieval": "bm25",
                }
            )
        return out
