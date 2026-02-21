from __future__ import annotations

import os
import secrets
import time
from collections import defaultdict, deque
from typing import Any

import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field

ALETHEIA_API_BASE = os.getenv("ALETHEIA_API_BASE", "http://127.0.0.1:40007")
BRIDGE_TOKEN = os.getenv("ALETHEIA_BRIDGE_TOKEN", "change-me")
REQUEST_TIMEOUT = float(os.getenv("ALETHEIA_BRIDGE_TIMEOUT", "30"))
RATE_LIMIT_PER_MIN = int(os.getenv("ALETHEIA_BRIDGE_RATE_LIMIT_PER_MIN", "60"))

app = FastAPI(title="Aletheia OpenClaw Bridge", version="0.2.0")

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


class ToolRequest(BaseModel):
    token: str
    query: str | None = None
    question: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    domain: str | None = None
    mode: str = "grounded"


def _auth(token: str) -> None:
    if not secrets.compare_digest(token, BRIDGE_TOKEN):
        raise HTTPException(status_code=401, detail="invalid bridge token")


def _rate_limit(client_id: str) -> None:
    now = time.time()
    bucket = _rate_buckets[client_id]

    while bucket and now - bucket[0] > 60:
        bucket.popleft()

    if len(bucket) >= RATE_LIMIT_PER_MIN:
        raise HTTPException(status_code=429, detail="rate limit exceeded")

    bucket.append(now)


def _forward(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    attempts = 3
    backoff = 0.35
    for i in range(attempts):
        try:
            res = requests.post(
                f"{ALETHEIA_API_BASE}{path}",
                json=payload,
                timeout=REQUEST_TIMEOUT,
            )
            res.raise_for_status()
            return res.json()
        except requests.RequestException:
            if i == attempts - 1:
                raise HTTPException(status_code=502, detail="upstream unavailable")
            time.sleep(backoff * (2**i))

    raise HTTPException(status_code=502, detail="upstream unavailable")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "openclaw-bridge"}


@app.post("/tool/search_knowledge")
def search_knowledge(req: ToolRequest, request: Request) -> dict[str, Any]:
    _auth(req.token)
    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")

    _rate_limit(request.client.host if request.client else "unknown")

    return _forward(
        "/search",
        {"query": req.query, "top_k": req.top_k, "domain": req.domain},
    )


@app.post("/tool/ask_knowledge")
def ask_knowledge(req: ToolRequest, request: Request) -> dict[str, Any]:
    _auth(req.token)
    if not req.question:
        raise HTTPException(status_code=400, detail="question is required")

    _rate_limit(request.client.host if request.client else "unknown")

    return _forward(
        "/ask",
        {"question": req.question, "top_k": req.top_k, "mode": req.mode},
    )
