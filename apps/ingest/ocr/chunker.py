from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_index: int
    text: str
    page_start: int
    page_end: int


def chunk_by_pages(pages: list[dict], pages_per_chunk: int = 2) -> list[Chunk]:
    """Simple provenance-preserving chunker based on page windows."""
    chunks: list[Chunk] = []
    idx = 0

    for i in range(0, len(pages), pages_per_chunk):
        window = pages[i : i + pages_per_chunk]
        text = "\n\n".join(p.get("text", "") for p in window).strip()
        if not text:
            continue
        chunks.append(
            Chunk(
                chunk_index=idx,
                text=text,
                page_start=int(window[0].get("page_start", 0)),
                page_end=int(window[-1].get("page_end", 0)),
            )
        )
        idx += 1

    return chunks
