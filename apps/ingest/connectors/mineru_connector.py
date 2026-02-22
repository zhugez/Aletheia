from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any


def parse_pdf_with_mineru(
    pdf_path: str | Path,
    out_dir: str | Path,
    *,
    backend: str | None = None,
    timeout: int | None = None,
) -> dict[str, Any]:
    """Run MinerU CLI and convert output into Aletheia-friendly payload.

    Requires `mineru` binary available in PATH.
    """
    src = Path(pdf_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        raise FileNotFoundError(src)

    backend = backend or os.getenv("INGEST_PDF_BACKEND", "pipeline")
    timeout = timeout or int(os.getenv("INGEST_PDF_TIMEOUT", "900"))

    cmd = ["mineru", "-p", str(src), "-o", str(out), "-b", backend]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise RuntimeError(f"MinerU failed ({proc.returncode}): {proc.stderr[:1200]}")

    # MinerU typically emits one or more markdown/json artifacts in output folder.
    md_files = sorted(out.rglob("*.md"))
    json_files = sorted(out.rglob("*.json"))

    text_parts: list[str] = []
    for p in md_files:
        try:
            text_parts.append(p.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            continue

    merged_text = "\n\n".join([t for t in text_parts if t.strip()])

    return {
        "source": src.name,
        "backend": backend,
        "doc_count": len(md_files),
        "documents": [
            {
                "doc_index": i,
                "text": (p.read_text(encoding="utf-8", errors="ignore") if p.exists() else ""),
                "file": str(p),
            }
            for i, p in enumerate(md_files)
        ],
        "merged_markdown": merged_text,
        "json_artifacts": [str(p) for p in json_files],
        "stdout": proc.stdout[-2000:],
    }
