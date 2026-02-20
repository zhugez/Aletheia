#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import uuid
from pathlib import Path
from typing import Any
from urllib import error, request


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ingest markdown chunks into Postgres/OpenSearch/Qdrant")
    p.add_argument("--input-dir", default="/tmp/aletheia_layout_output")
    p.add_argument("--max-chars", type=int, default=800)
    p.add_argument("--file", default=None, help="Ingest only one markdown filename inside --input-dir")
    p.add_argument("--skip-qdrant", action="store_true", help="Skip vector ingest temporarily")
    return p.parse_args()


def chunk_text(text: str, max_chars: int) -> list[str]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    chunks: list[str] = []
    buf = ""
    for block in blocks:
        if len(buf) + len(block) + 2 <= max_chars:
            buf = (buf + "\n\n" + block).strip()
        else:
            if buf:
                chunks.append(buf)
            buf = block
    if buf:
        chunks.append(buf)
    return chunks


def parse_meta(path: Path) -> tuple[str, str, int]:
    stem = path.stem
    title = stem.replace("_", " ")
    chapter = "unknown"
    page = 1
    m_ch = re.search(r"chapter[_\- ]?(\d+)", stem, re.IGNORECASE)
    if m_ch:
        chapter = m_ch.group(1)
    m_pg = re.search(r"page[_\- ]?(\d+)", stem, re.IGNORECASE)
    if m_pg:
        page = int(m_pg.group(1))
    return title, chapter, page


def embed(text: str, size: int = 64) -> list[float]:
    vec = [0.0] * size
    for token in text.lower().split():
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:2], "big") % size
        sign = -1.0 if digest[2] % 2 else 1.0
        vec[idx] += sign * (1.0 + (digest[3] / 255.0))
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def http_json(method: str, url: str, body: dict[str, Any] | str | None = None, content_type: str = "application/json") -> dict[str, Any]:
    if isinstance(body, dict):
        data = json.dumps(body).encode("utf-8")
    elif isinstance(body, str):
        data = body.encode("utf-8")
    else:
        data = None
    req = request.Request(url, data=data, method=method, headers={"Content-Type": content_type})
    with request.urlopen(req, timeout=10) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def wait_http_ready(url: str, tries: int = 20, sleep_s: float = 1.5) -> bool:
    import time

    for _ in range(tries):
        try:
            http_json("GET", url)
            return True
        except Exception:
            time.sleep(sleep_s)
    return False


def ingest_postgres(postgres_url: str, source_id: str, title: str, chunks: list[dict[str, Any]]) -> int:
    try:
        import psycopg
    except Exception:
        print("[warn] psycopg not installed; skipping Postgres ingest")
        return 0

    inserted = 0
    with psycopg.connect(postgres_url) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                insert into sources (id, source_type, title)
                values (%s, %s, %s)
                on conflict (id) do update set title = excluded.title
                """,
                (source_id, "book", title),
            )
            for c in chunks:
                cur.execute(
                    """
                    insert into chunks (id, source_id, chapter, page_start, page_end, chunk_index, text_content, token_count)
                    values (%s, %s, %s, %s, %s, %s, %s, %s)
                    on conflict (id) do update set text_content = excluded.text_content
                    """,
                    (
                        c["chunk_id"],
                        source_id,
                        c["chapter"],
                        c["page_start"],
                        c["page_end"],
                        c["chunk_index"],
                        c["text_content"],
                        len(c["text_content"].split()),
                    ),
                )
                inserted += 1
        conn.commit()
    return inserted


def ingest_opensearch(base_url: str, index: str, chunks: list[dict[str, Any]]) -> int:
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
        http_json("PUT", f"{base_url.rstrip('/')}/{index}", mapping)
    except Exception:
        pass

    lines = []
    for c in chunks:
        lines.append(json.dumps({"index": {"_index": index, "_id": c["chunk_id"]}}))
        lines.append(json.dumps(c))
    payload = "\n".join(lines) + "\n"
    res = http_json("POST", f"{base_url.rstrip('/')}/_bulk", payload, content_type="application/x-ndjson")
    if res.get("errors"):
        raise RuntimeError("OpenSearch bulk ingest returned errors")
    return len(chunks)


def ingest_qdrant(base_url: str, collection: str, chunks: list[dict[str, Any]]) -> int:
    # Ensure collection exists with expected vector size; ignore already-exists or conflict variants.
    try:
        http_json(
            "PUT",
            f"{base_url.rstrip('/')}/collections/{collection}",
            {"vectors": {"size": 64, "distance": "Cosine"}},
        )
    except error.HTTPError as e:
        if e.code not in (400, 409):
            raise

    points = []
    for c in chunks:
        points.append(
            {
                "id": c["chunk_id"],
                "vector": embed(c["text_content"]),
                "payload": c,
            }
        )
    http_json("PUT", f"{base_url.rstrip('/')}/collections/{collection}/points?wait=true", {"points": points})
    return len(points)


def main() -> int:
    args = parse_args()
    input_dir = Path(args.input_dir)
    files = sorted(input_dir.glob("*.md"))
    if args.file:
        files = [f for f in files if f.name == args.file]
    if not files:
        print(f"No markdown files found in {input_dir}")
        return 1

    postgres_url = os.getenv("POSTGRES_URL", "postgresql://aletheia:aletheia@localhost:5432/aletheia")
    opensearch_url = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
    opensearch_index = os.getenv("OPENSEARCH_INDEX", "aletheia_chunks")
    qdrant_collection = os.getenv("QDRANT_COLLECTION", "aletheia_chunks")

    # Warm up external engines to avoid cold-start flakiness right after compose up.
    wait_http_ready(f"{opensearch_url.rstrip('/')}/_cluster/health")
    if not args.skip_qdrant:
        wait_http_ready(f"{qdrant_url.rstrip('/')}/collections")

    total_pg = total_os = total_qd = 0
    for f in files:
        title, chapter, page = parse_meta(f)
        source_id = str(uuid.uuid5(uuid.NAMESPACE_URL, f"file://{f}"))
        text = f.read_text(encoding="utf-8", errors="ignore")
        chunked = chunk_text(text, args.max_chars)

        chunks: list[dict[str, Any]] = []
        for i, chunk in enumerate(chunked):
            chunk_id = str(uuid.uuid5(uuid.NAMESPACE_OID, f"{source_id}:{i}"))
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "source_id": source_id,
                    "title": title,
                    "chapter": chapter,
                    "page_start": page,
                    "page_end": page,
                    "chunk_index": i,
                    "text_content": chunk,
                }
            )

        try:
            total_pg += ingest_postgres(postgres_url, source_id, title, chunks)
        except Exception as e:
            print(f"[warn] Postgres ingest failed for {f.name}: {e}")
        try:
            total_os += ingest_opensearch(opensearch_url, opensearch_index, chunks)
        except Exception as e:
            print(f"[warn] OpenSearch ingest failed for {f.name}: {e}")
        if not args.skip_qdrant:
            try:
                total_qd += ingest_qdrant(qdrant_url, qdrant_collection, chunks)
            except Exception as e:
                print(f"[warn] Qdrant ingest failed for {f.name}: {e}")
        print(f"Ingested {len(chunks)} chunks from {f.name}")

    print(f"Done. Postgres={total_pg} OpenSearch={total_os} Qdrant={total_qd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
