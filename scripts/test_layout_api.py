from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from apps.ingest.connectors.aistudio_layout import parse_layout


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_layout_api.py <file_path>")
        return 1

    src = Path(sys.argv[1])
    out_dir = Path(os.getenv("ALETHEIA_LAYOUT_OUTPUT_DIR", "/tmp/aletheia_layout_output"))
    out_dir.mkdir(parents=True, exist_ok=True)

    parsed = parse_layout(src)

    summary = {
        "source": parsed["source"],
        "doc_count": parsed["doc_count"],
        "text_chars": [len(d.get("text", "")) for d in parsed["documents"]],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    for doc in parsed["documents"]:
        md_file = out_dir / f"{src.stem}_doc_{doc['doc_index']}.md"
        md_file.write_text(doc.get("text", ""), encoding="utf-8")

    print(f"Saved markdown to: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
