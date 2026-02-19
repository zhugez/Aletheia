# PaddleOCR Pipeline

## Purpose
Improve OCR quality for scanned books, especially Vietnamese/English mixed content.

## Files
- `paddle_adapter.py` — OCR adapter wrapper
- `normalize.py` — post-OCR cleanup helpers
- `pdf_pipeline.py` — PDF rasterization + per-page OCR with provenance
- `chunker.py` — page-window chunking preserving page_start/page_end

## Dependencies
```bash
pip install paddleocr pymupdf
```

## Usage (PDF end-to-end)
```bash
python scripts/ingest_pdf_ocr_demo.py /path/to/book.pdf vi
```

## Output highlights
- per-page OCR records with `page`, `ocr_confidence`, `page_start/page_end`
- merged text
- provenance-preserving chunks
