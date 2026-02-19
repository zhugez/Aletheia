from __future__ import annotations

import os
from typing import Any

import requests
from mcp.server.fastmcp import FastMCP

ALETHEIA_API_BASE = os.getenv("ALETHEIA_API_BASE", "http://127.0.0.1:8080")
API_KEY = os.getenv("ALETHEIA_API_KEY", "")

mcp = FastMCP("aletheia-mcp")


def _headers() -> dict[str, str]:
    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"
    return headers


def _post(path: str, payload: dict[str, Any]) -> dict[str, Any]:
    res = requests.post(
        f"{ALETHEIA_API_BASE}{path}",
        json=payload,
        headers=_headers(),
        timeout=30,
    )
    res.raise_for_status()
    return res.json()


@mcp.tool()
def search_knowledge(query: str, top_k: int = 5, domain: str | None = None) -> dict[str, Any]:
    """Search Aletheia knowledge base and return citation-ready chunks."""
    return _post("/search", {"query": query, "top_k": top_k, "domain": domain})


@mcp.tool()
def ask_knowledge(question: str, top_k: int = 5, mode: str = "grounded") -> dict[str, Any]:
    """Ask a grounded question and get answer + citations."""
    return _post("/ask", {"question": question, "top_k": top_k, "mode": mode})


@mcp.tool()
def get_source(source_id: str) -> dict[str, Any]:
    """Get source metadata (placeholder until metadata endpoint is implemented)."""
    return {
        "source_id": source_id,
        "status": "not_implemented",
        "message": "Implement /sources/{source_id} in API service.",
    }


@mcp.tool()
def ingest_source(source_uri: str, source_type: str = "book", metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    """Queue a source for ingestion (placeholder bridge)."""
    return {
        "status": "queued_stub",
        "source_uri": source_uri,
        "source_type": source_type,
        "metadata": metadata or {},
    }


@mcp.tool()
def ingest_status(job_id: str) -> dict[str, Any]:
    """Check ingest job status (placeholder until queue API is implemented)."""
    return {
        "job_id": job_id,
        "status": "not_implemented",
    }


if __name__ == "__main__":
    mcp.run()
