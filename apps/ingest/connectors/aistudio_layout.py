from __future__ import annotations

import base64
import os
import time
from pathlib import Path
from typing import Any

import requests

API_URL_DEFAULT = "https://kdv9r7ndp1a2v19f.aistudio-app.com/layout-parsing"


def _b64_file(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def _infer_file_type(path: Path) -> int:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return 0
    if ext in {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}:
        return 1
    raise ValueError(f"Unsupported file extension: {ext}")


def _post_with_retry(url: str, headers: dict[str, str], payload: dict[str, Any]) -> dict[str, Any]:
    retries = int(os.getenv("ALETHEIA_LAYOUT_RETRIES", "3"))
    timeout = float(os.getenv("ALETHEIA_LAYOUT_TIMEOUT", "90"))
    backoff = 1.0

    last_err: Exception | None = None
    for i in range(retries):
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=timeout)
            if res.status_code >= 500:
                raise RuntimeError(f"upstream 5xx: {res.status_code} {res.text[:300]}")
            if res.status_code != 200:
                raise RuntimeError(f"upstream error: {res.status_code} {res.text[:500]}")
            return res.json()
        except Exception as e:  # pragma: no cover
            last_err = e
            if i == retries - 1:
                break
            time.sleep(backoff)
            backoff *= 2

    raise RuntimeError(f"Layout API failed after retries: {last_err}")


def parse_layout(
    file_path: str | Path,
    *,
    api_url: str | None = None,
    token: str | None = None,
    use_doc_orientation_classify: bool = False,
    use_doc_unwarping: bool = False,
    use_chart_recognition: bool = False,
) -> dict[str, Any]:
    src = Path(file_path)
    if not src.exists():
        raise FileNotFoundError(src)

    api_url = api_url or os.getenv("ALETHEIA_LAYOUT_API_URL", API_URL_DEFAULT)
    token = token or os.getenv("ALETHEIA_LAYOUT_API_TOKEN")
    if not token:
        raise RuntimeError("Missing ALETHEIA_LAYOUT_API_TOKEN")

    payload = {
        "file": _b64_file(src),
        "fileType": _infer_file_type(src),
        "useDocOrientationClassify": use_doc_orientation_classify,
        "useDocUnwarping": use_doc_unwarping,
        "useChartRecognition": use_chart_recognition,
    }

    headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/json",
    }

    data = _post_with_retry(api_url, headers, payload)
    result = data.get("result", {})
    items = result.get("layoutParsingResults", []) or []

    docs: list[dict[str, Any]] = []
    for idx, item in enumerate(items):
        md = item.get("markdown", {}) or {}
        docs.append(
            {
                "doc_index": idx,
                "text": md.get("text", ""),
                "images": md.get("images", {}),
                "output_images": item.get("outputImages", {}),
            }
        )

    return {
        "source": src.name,
        "doc_count": len(docs),
        "documents": docs,
        "raw_result": result,
    }
