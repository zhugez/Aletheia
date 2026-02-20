#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from urllib import request


API = "http://127.0.0.1:8080"


def post(path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(
        f"{API}{path}",
        data=data,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fail(msg: str) -> int:
    print(f"[FAIL] {msg}")
    return 1


def main() -> int:
    search = post("/search", {"query": "WordPress scaling performance", "top_k": 3})
    results = search.get("results", [])
    if not results:
        return fail("/search returned empty results")

    required = {"title", "chapter", "page_start", "page_end", "chunk_id", "score", "text"}
    for i, row in enumerate(results):
        missing = [k for k in required if k not in row]
        if missing:
            return fail(f"result[{i}] missing fields: {missing}")

    ask = post("/ask", {"question": "Why WordPress was not enough?", "top_k": 3, "mode": "grounded"})
    if ask.get("insufficient_evidence") is True:
        return fail("/ask returned insufficient_evidence=true")
    if len(ask.get("citations", [])) == 0:
        return fail("/ask returned no citations")

    print("[PASS] retrieval real-case benchmark")
    print(json.dumps({
        "search_count": len(results),
        "top1_title": results[0].get("title"),
        "ask_confidence": ask.get("confidence"),
        "ask_citations": len(ask.get("citations", [])),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
