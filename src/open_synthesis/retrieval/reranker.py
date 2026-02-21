"""Cross-encoder reranker placeholder."""

from __future__ import annotations

from open_synthesis.types import RetrievedChunk


def rerank(
    query: str,
    chunks: list[RetrievedChunk],
    n_results: int = 20,
) -> list[RetrievedChunk]:
    """Rerank chunks using a cross-encoder model.

    Currently a passthrough — returns chunks in their existing order,
    truncated to n_results. Replace with a cross-encoder (e.g.
    cross-encoder/ms-marco-MiniLM-L-6-v2) for production use.
    """
    return chunks[:n_results]
