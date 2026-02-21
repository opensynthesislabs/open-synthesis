"""BM25 sparse keyword retrieval."""

from __future__ import annotations

from rank_bm25 import BM25Okapi

from open_synthesis.types import Chunk, RetrievedChunk


class BM25Index:
    """In-memory BM25 index over chunk texts."""

    def __init__(self, chunks: list[Chunk]) -> None:
        self._chunks = chunks
        tokenized = [c.text.lower().split() for c in chunks]
        self._bm25 = BM25Okapi(tokenized)

    def search(self, query: str, n_results: int = 20) -> list[RetrievedChunk]:
        tokenized_query = query.lower().split()
        scores = self._bm25.get_scores(tokenized_query)

        scored_pairs = sorted(
            zip(scores, self._chunks),
            key=lambda x: x[0],
            reverse=True,
        )[:n_results]

        return [
            RetrievedChunk(chunk=chunk, score=float(score), retrieval_method="sparse")
            for score, chunk in scored_pairs
            if score > 0
        ]
