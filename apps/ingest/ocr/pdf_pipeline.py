from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .normalize import normalize_ocr_text
from .paddle_adapter import PaddleOCRAdapter


@dataclass
class PageOCRRecord:
    page: int
    text: str
    ocr_confidence: float
    page_start: int
    page_end: int


def rasterize_pdf_pages(pdf_path: str | Path, out_dir: str | Path, dpi: int = 180) -> list[Path]:
    """Rasterize PDF pages to PNG using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except Exception as e:  # pragma: no cover
        raise RuntimeError("PyMuPDF is required. Install with `pip install pymupdf`.") from e

    src = Path(pdf_path)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(src)
    image_paths: list[Path] = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_path = out / f"page_{i:04d}.png"
        pix.save(str(img_path))
        image_paths.append(img_path)

    doc.close()
    return image_paths


def extract_pdf_with_paddle(
    pdf_path: str | Path,
    temp_dir: str | Path,
    lang: str = "vi",
    max_pages: int | None = None,
) -> dict[str, Any]:
    """OCR a PDF by rasterizing pages then applying PaddleOCR per page."""
    pages = rasterize_pdf_pages(pdf_path, temp_dir)
    if max_pages is not None:
        pages = pages[:max_pages]

    ocr = PaddleOCRAdapter(lang=lang)
    records: list[PageOCRRecord] = []

    for idx, img in enumerate(pages, start=1):
        raw = ocr.extract_file(img)
        cleaned = normalize_ocr_text(raw["text"])
        records.append(
            PageOCRRecord(
                page=idx,
                text=cleaned,
                ocr_confidence=float(raw.get("ocr_confidence", 0.0)),
                page_start=idx,
                page_end=idx,
            )
        )

    full_text = "\n\n".join(r.text for r in records if r.text)
    avg_conf = sum(r.ocr_confidence for r in records) / len(records) if records else 0.0

    return {
        "source": Path(pdf_path).name,
        "page_count": len(records),
        "avg_ocr_confidence": round(avg_conf, 4),
        "text": full_text,
        "pages": [r.__dict__ for r in records],
    }
