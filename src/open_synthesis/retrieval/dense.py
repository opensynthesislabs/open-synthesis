"""Dense vector retrieval via sentence-transformers + ChromaDB."""

from __future__ import annotations

from open_synthesis.corpus.store import VectorStore
from open_synthesis.types import RetrievedChunk


def dense_search(
    store: VectorStore,
    domain: str,
    query: str,
    n_results: int = 20,
) -> list[RetrievedChunk]:
    """Embed query and search ChromaDB for nearest neighbors."""
    return store.query(domain, query, n_results=n_results)
