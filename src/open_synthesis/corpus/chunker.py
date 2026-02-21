"""Text chunking at paragraph level with metadata inheritance."""

from __future__ import annotations

import hashlib
from typing import Any

from open_synthesis.types import Chunk, Document


def _chunk_id(document_id: str, index: int) -> str:
    raw = f"{document_id}:{index}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def chunk_document(
    doc: Document,
    min_chunk_length: int = 50,
) -> list[Chunk]:
    """Split a document into paragraph-level chunks.

    Uses the full_text if available, otherwise falls back to the abstract.
    Each chunk inherits document metadata (source_type, authors, year, doi).
    """
    text = doc.full_text or doc.abstract
    if not text:
        return []

    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    # Merge very short paragraphs with the next one
    merged: list[str] = []
    buffer = ""
    for para in paragraphs:
        if buffer:
            buffer = buffer + "\n\n" + para
        else:
            buffer = para
        if len(buffer) >= min_chunk_length:
            merged.append(buffer)
            buffer = ""
    if buffer:
        if merged:
            merged[-1] = merged[-1] + "\n\n" + buffer
        else:
            merged.append(buffer)

    inherited_meta: dict[str, Any] = {
        "source_type": doc.source_type,
        "authors": ", ".join(doc.authors) if doc.authors else "Unknown",
        "year": str(doc.year) if doc.year else "n.d.",
        "doi": doc.doi or "",
        "title": doc.title,
        "source_id": doc.source_id,
    }

    return [
        Chunk(
            chunk_id=_chunk_id(doc.source_id, i),
            document_id=doc.source_id,
            text=para,
            index=i,
            metadata=inherited_meta,
        )
        for i, para in enumerate(merged)
    ]
