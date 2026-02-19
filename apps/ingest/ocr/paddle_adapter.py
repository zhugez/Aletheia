from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class OCRPageResult:
    page: int
    text: str
    confidence: float


class PaddleOCRAdapter:
    """PaddleOCR adapter (scaffold).

    Requires: pip install paddleocr
    """

    def __init__(self, lang: str = "vi") -> None:
        self.lang = lang
        self._ocr = None

    def _lazy_init(self) -> None:
        if self._ocr is not None:
            return
        try:
            from paddleocr import PaddleOCR  # type: ignore
        except Exception as e:  # pragma: no cover
            raise RuntimeError(
                "PaddleOCR is not installed. Install with `pip install paddleocr`."
            ) from e

        self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang)

    def extract_file(self, file_path: str | Path) -> dict[str, Any]:
        self._lazy_init()
        fp = str(file_path)

        # NOTE: For PDF, PaddleOCR can process page images if rasterized first.
        # This scaffold expects image paths or pre-rasterized pages for now.
        result = self._ocr.ocr(fp, cls=True)

        lines: list[str] = []
        confs: list[float] = []
        for block in result or []:
            for item in block or []:
                txt = item[1][0]
                conf = float(item[1][1])
                lines.append(txt)
                confs.append(conf)

        avg_conf = sum(confs) / len(confs) if confs else 0.0

        return {
            "source": os.path.basename(fp),
            "text": "\n".join(lines),
            "ocr_confidence": round(avg_conf, 4),
            "line_count": len(lines),
        }
