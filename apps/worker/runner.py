from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Any


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}"
        )


def process_ingest_job(payload: dict[str, Any]) -> dict[str, Any]:
    """Background ingest job entrypoint (real ingest flow).

    Flow:
    1) read uploaded local file URI
    2) run MinerU parse -> merged markdown
    3) index markdown chunks into Postgres/OpenSearch/Qdrant
    """
    source_uri = payload.get("source_uri")
    source_type = payload.get("source_type", "book")
    metadata = payload.get("metadata", {})

    if not source_uri:
        return {"ok": False, "reason": "missing_source_uri"}

    if not str(source_uri).startswith("file://"):
        return {"ok": False, "reason": "unsupported_source_uri", "source_uri": source_uri}

    local_path = Path(str(source_uri).replace("file://", "", 1))
    if not local_path.exists():
        return {"ok": False, "reason": "source_not_found", "source_uri": source_uri}

    out_dir = Path(os.getenv("INGEST_OUTPUT_DIR", "/shared/output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    backend = os.getenv("INGEST_PDF_BACKEND", "pipeline")
    max_chars = os.getenv("INGEST_MAX_CHARS", "800")

    # scripts live under /app/scripts in the worker image (repo root copied into /app)
    _run([
        "python",
        "/app/scripts/ingest_pdf_full_mineru.py",
        str(local_path),
        "--out",
        str(out_dir),
        "--backend",
        backend,
        "--max-chars",
        str(max_chars),
    ])

    return {
        "ok": True,
        "stage": "indexed",
        "source_uri": source_uri,
        "source_type": source_type,
        "metadata": metadata,
        "engine": "mineru",
    }
