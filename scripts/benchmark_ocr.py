from __future__ import annotations

import json
import sys
from pathlib import Path

from apps.ingest.ocr.normalize import normalize_ocr_text


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/benchmark_ocr.py <image_or_page_path>")
        return 1

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"Not found: {target}")
        return 1

    from apps.ingest.ocr.paddle_adapter import PaddleOCRAdapter

    ocr = PaddleOCRAdapter(lang="vi")
    raw = ocr.extract_file(target)
    raw["clean_text_preview"] = normalize_ocr_text(raw["text"])[:800]

    print(json.dumps(raw, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
