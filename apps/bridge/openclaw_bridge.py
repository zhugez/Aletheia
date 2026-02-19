from __future__ import annotations

import os
from typing import Any

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ALETHEIA_API_BASE = os.getenv("ALETHEIA_API_BASE", "http://127.0.0.1:8080")
BRIDGE_TOKEN = os.getenv("ALETHEIA_BRIDGE_TOKEN", "change-me")

app = FastAPI(title="Aletheia OpenClaw Bridge", version="0.1.0")


class ToolRequest(BaseModel):
    token: str
    query: str | None = None
    question: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    domain: str | None = None
    mode: str = "grounded"


def _auth(token: str) -> None:
    if token != BRIDGE_TOKEN:
        raise HTTPException(status_code=401, detail="invalid bridge token")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "openclaw-bridge"}


@app.post("/tool/search_knowledge")
def search_knowledge(req: ToolRequest) -> dict[str, Any]:
    _auth(req.token)
    if not req.query:
        raise HTTPException(status_code=400, detail="query is required")

    res = requests.post(
        f"{ALETHEIA_API_BASE}/search",
        json={"query": req.query, "top_k": req.top_k, "domain": req.domain},
        timeout=30,
    )
    res.raise_for_status()
    return res.json()


@app.post("/tool/ask_knowledge")
def ask_knowledge(req: ToolRequest) -> dict[str, Any]:
    _auth(req.token)
    if not req.question:
        raise HTTPException(status_code=400, detail="question is required")

    res = requests.post(
        f"{ALETHEIA_API_BASE}/ask",
        json={"question": req.question, "top_k": req.top_k, "mode": req.mode},
        timeout=30,
    )
    res.raise_for_status()
    return res.json()
