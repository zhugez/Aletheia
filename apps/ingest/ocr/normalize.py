from __future__ import annotations

import re


def normalize_ocr_text(text: str) -> str:
    """Basic OCR cleanup for vi/en text."""
    # Collapse excessive whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Fix common OCR split around punctuation
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)

    return text.strip()
