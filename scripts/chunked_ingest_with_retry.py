from __future__ import annotations

import argparse
import base64
import json
import time
from io import BytesIO
from pathlib import Path

import requests
from pypdf import PdfReader, PdfWriter

API_URL = "https://kdv9r7ndp1a2v19f.aistudio-app.com/layout-parsing"


def call_api(pdf_bytes: bytes, token: str, timeout: int) -> dict:
    payload = {
        "file": base64.b64encode(pdf_bytes).decode("ascii"),
        "fileType": 0,
        "useDocOrientationClassify": False,
        "useDocUnwarping": False,
        "useChartRecognition": False,
    }
    headers = {"Authorization": f"token {token}", "Content-Type": "application/json"}
    r = requests.post(API_URL, json=payload, headers=headers, timeout=timeout)
    r.raise_for_status()
    return r.json()


def chunk_pdf(path: Path, chunk_pages: int):
    reader = PdfReader(str(path))
    total = len(reader.pages)
    for start in range(0, total, chunk_pages):
        end = min(start + chunk_pages, total)
        w = PdfWriter()
        for i in range(start, end):
            w.add_page(reader.pages[i])
        bio = BytesIO()
        w.write(bio)
        yield start + 1, end, bio.getvalue(), total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--token", required=True)
    ap.add_argument("--chunk-pages", type=int, default=4)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--out", default="/tmp/aletheia_layout_output")
    args = ap.parse_args()

    src = Path(args.pdf)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    state_file = out_dir / f"{src.stem}.state.json"
    merged_md = out_dir / f"{src.stem}.merged.md"

    state = {"source": src.name, "chunks": []}
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))

    done_ranges = {(c["start"], c["end"]) for c in state.get("chunks", []) if c.get("status") == "ok"}

    merged_parts = []
    for start, end, chunk_bytes, total in chunk_pdf(src, args.chunk_pages):
        if (start, end) in done_ranges:
            continue

        ok = False
        last_err = ""
        for i in range(args.retries):
            try:
                data = call_api(chunk_bytes, args.token, args.timeout)
                lpr = data.get("result", {}).get("layoutParsingResults", [])
                text = "\n\n".join(((x.get("markdown", {}) or {}).get("text", "") for x in lpr))
                part_file = out_dir / f"{src.stem}_{start}_{end}.md"
                part_file.write_text(text, encoding="utf-8")
                state["chunks"].append({"start": start, "end": end, "status": "ok", "pages_total": total, "file": str(part_file)})
                merged_parts.append(text)
                ok = True
                break
            except Exception as e:
                last_err = str(e)
                time.sleep(1.5 * (2**i))

        if not ok:
            state["chunks"].append({"start": start, "end": end, "status": "failed", "error": last_err})

        state_file.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    # rebuild merged file from all successful chunks in order
    ok_chunks = sorted([c for c in state["chunks"] if c.get("status") == "ok"], key=lambda x: x["start"])
    all_text = []
    for c in ok_chunks:
        p = Path(c["file"])
        if p.exists():
            all_text.append(p.read_text(encoding="utf-8"))
    merged_md.write_text("\n\n".join(all_text), encoding="utf-8")

    print(json.dumps({
        "source": src.name,
        "chunks_ok": len(ok_chunks),
        "chunks_total": len(list(chunk_pdf(src, args.chunk_pages))),
        "state": str(state_file),
        "merged": str(merged_md),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
