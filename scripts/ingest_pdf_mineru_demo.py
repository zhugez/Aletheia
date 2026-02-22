from __future__ import annotations

import argparse
import json
from pathlib import Path

from apps.ingest.connectors.mineru_connector import parse_pdf_with_mineru


def main() -> int:
    ap = argparse.ArgumentParser(description="Run MinerU on one PDF and emit merged markdown")
    ap.add_argument("pdf")
    ap.add_argument("--out", default="/tmp/aletheia_mineru_output")
    ap.add_argument("--backend", default="pipeline", help="mineru backend, e.g. pipeline")
    args = ap.parse_args()

    src = Path(args.pdf)
    out = Path(args.out)

    result = parse_pdf_with_mineru(src, out, backend=args.backend)

    merged = out / f"{src.stem}.merged.md"
    merged.write_text(result.get("merged_markdown", ""), encoding="utf-8")

    print(json.dumps({
        "source": src.name,
        "backend": result.get("backend"),
        "doc_count": result.get("doc_count"),
        "merged": str(merged),
        "json_artifacts": result.get("json_artifacts", []),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
