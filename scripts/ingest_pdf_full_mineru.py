from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


def run(cmd: list[str]) -> None:
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\nSTDOUT:\n{p.stdout}\nSTDERR:\n{p.stderr}")


def main() -> int:
    ap = argparse.ArgumentParser(description="End-to-end PDF ingest: MinerU parse -> markdown index")
    ap.add_argument("pdf")
    ap.add_argument("--out", default="/tmp/aletheia_mineru_output")
    ap.add_argument("--backend", default="pipeline")
    ap.add_argument("--max-chars", type=int, default=800)
    args = ap.parse_args()

    pdf = Path(args.pdf)
    if not pdf.exists():
        raise FileNotFoundError(pdf)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # Resolve script paths relative to this file (repo root /app/scripts/)
    _scripts = Path(__file__).resolve().parent

    # Step 1: parse with MinerU
    run([
        "python3",
        str(_scripts / "ingest_pdf_mineru_demo.py"),
        str(pdf),
        "--out",
        str(out),
        "--backend",
        args.backend,
    ])

    merged_md = out / f"{pdf.stem}.merged.md"
    if not merged_md.exists() or merged_md.stat().st_size == 0:
        raise RuntimeError(f"Merged markdown not found or empty: {merged_md}")

    # Step 2: index markdown into retrieval stores
    run([
        "python3",
        str(_scripts / "ingest_markdown_chunks.py"),
        "--input-dir",
        str(out),
        "--file",
        merged_md.name,
        "--max-chars",
        str(args.max_chars),
    ])

    print(json.dumps({
        "ok": True,
        "source": pdf.name,
        "merged_markdown": str(merged_md),
        "indexed": True,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
