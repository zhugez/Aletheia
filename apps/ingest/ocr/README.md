# PaddleOCR Adapter (Scaffold)

## Purpose
Improve OCR quality for scanned books, especially Vietnamese/English mixed content.

## Files
- `paddle_adapter.py` — OCR adapter wrapper
- `normalize.py` — post-OCR cleanup helpers

## Usage (example)
```python
from apps.ingest.ocr.paddle_adapter import PaddleOCRAdapter
from apps.ingest.ocr.normalize import normalize_ocr_text

ocr = PaddleOCRAdapter(lang="vi")
raw = ocr.extract_file("./sample_page.png")
clean = normalize_ocr_text(raw["text"])
```

## Notes
- Current scaffold expects image input (or pre-rasterized PDF pages).
- Next step: add PDF rasterization pipeline + per-page provenance.
