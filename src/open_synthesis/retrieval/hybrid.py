"""Hybrid retrieval via reciprocal rank fusion."""

from __future__ import annotations

from open_synthesis.types import RetrievedChunk


def reciprocal_rank_fusion(
    result_lists: list[list[RetrievedChunk]],
    weights: list[float] | None = None,
    k: int = 60,
    n_results: int = 20,
) -> list[RetrievedChunk]:
    """Combine multiple ranked result lists using reciprocal rank fusion.

    RRF score = sum over lists of: weight / (k + rank)
    where rank is 1-indexed position in the list.
    """
    if not result_lists:
        return []

    if weights is None:
        weights = [1.0] * len(result_lists)

    # Track best chunk per chunk_id and accumulate RRF scores
    scores: dict[str, float] = {}
    best_chunk: dict[str, RetrievedChunk] = {}

    for result_list, weight in zip(result_lists, weights):
        for rank, rc in enumerate(result_list, start=1):
            cid = rc.chunk.chunk_id
            rrf_score = weight / (k + rank)
            scores[cid] = scores.get(cid, 0.0) + rrf_score
            if cid not in best_chunk:
                best_chunk[cid] = rc

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:n_results]

    return [
        RetrievedChunk(
            chunk=best_chunk[cid].chunk,
            score=score,
            retrieval_method="hybrid",
        )
        for cid, score in ranked
    ]
