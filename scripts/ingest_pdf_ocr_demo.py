from __future__ import annotations

import json
import sys
from pathlib import Path

from apps.ingest.ocr.chunker import chunk_by_pages
from apps.ingest.ocr.pdf_pipeline import extract_pdf_with_paddle


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/ingest_pdf_ocr_demo.py <pdf_path> [lang]")
        return 1

    pdf_path = Path(sys.argv[1])
    lang = sys.argv[2] if len(sys.argv) > 2 else "vi"

    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        return 1

    temp_dir = Path("/tmp/aletheia_ocr_pages") / pdf_path.stem
    result = extract_pdf_with_paddle(pdf_path, temp_dir, lang=lang)

    chunks = chunk_by_pages(result["pages"], pages_per_chunk=2)
    payload = {
        "source": result["source"],
        "page_count": result["page_count"],
        "avg_ocr_confidence": result["avg_ocr_confidence"],
        "chunk_count": len(chunks),
        "chunks": [c.__dict__ for c in chunks[:5]],
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
