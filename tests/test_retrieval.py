"""Tests for hybrid retrieval logic."""

from __future__ import annotations

from open_synthesis.retrieval.hybrid import reciprocal_rank_fusion
from open_synthesis.types import Chunk, RetrievedChunk


def _make_chunk(cid: str, text: str = "test") -> RetrievedChunk:
    chunk = Chunk(chunk_id=cid, document_id="doc1", text=text, index=0, metadata={})
    return RetrievedChunk(chunk=chunk, score=1.0, retrieval_method="test")


def test_rrf_empty():
    assert reciprocal_rank_fusion([]) == []


def test_rrf_single_list():
    results = [_make_chunk("a"), _make_chunk("b"), _make_chunk("c")]
    fused = reciprocal_rank_fusion([results])
    assert len(fused) == 3
    assert fused[0].chunk.chunk_id == "a"


def test_rrf_overlap_boosts():
    list1 = [_make_chunk("a"), _make_chunk("b"), _make_chunk("c")]
    list2 = [_make_chunk("b"), _make_chunk("a"), _make_chunk("d")]

    fused = reciprocal_rank_fusion([list1, list2], n_results=4)
    ids = [rc.chunk.chunk_id for rc in fused]

    # Both "a" and "b" appear in both lists, so they should rank highest
    assert "a" in ids[:2]
    assert "b" in ids[:2]


def test_rrf_weights():
    list1 = [_make_chunk("a")]
    list2 = [_make_chunk("b")]

    # Heavily weight list1
    fused = reciprocal_rank_fusion([list1, list2], weights=[10.0, 1.0], n_results=2)
    assert fused[0].chunk.chunk_id == "a"


def test_rrf_n_results_limit():
    results = [_make_chunk(str(i)) for i in range(10)]
    fused = reciprocal_rank_fusion([results], n_results=3)
    assert len(fused) == 3


def test_rrf_all_hybrid_method():
    list1 = [_make_chunk("a")]
    fused = reciprocal_rank_fusion([list1])
    assert all(rc.retrieval_method == "hybrid" for rc in fused)
