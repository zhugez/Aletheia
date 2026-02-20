from __future__ import annotations

from typing import Any


def process_ingest_job(payload: dict[str, Any]) -> dict[str, Any]:
    """Background ingest job entrypoint.

    Current behavior is intentionally safe and minimal:
    - validates payload
    - returns accepted metadata for orchestration

    Hook real ingest pipeline here (OCR/layout/chunk/index) in next phase.
    """
    source_uri = payload.get("source_uri")
    source_type = payload.get("source_type", "book")
    metadata = payload.get("metadata", {})

    if not source_uri:
        return {"ok": False, "reason": "missing_source_uri"}

    return {
        "ok": True,
        "stage": "accepted",
        "source_uri": source_uri,
        "source_type": source_type,
        "metadata": metadata,
    }
