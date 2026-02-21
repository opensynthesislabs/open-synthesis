"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from open_synthesis.config import Settings, load_settings
from open_synthesis.types import Chunk, Document, RetrievedChunk


@pytest.fixture
def sample_document() -> Document:
    return Document(
        source_id="test:001",
        source_type="test",
        title="Effects of Psilocybin on Major Depressive Disorder",
        authors=["Davis AK", "Barrett FS", "May DG"],
        year=2021,
        doi="10.1001/jamapsychiatry.2020.3285",
        abstract="This randomized clinical trial found that psilocybin-assisted therapy was efficacious in producing large, rapid, and sustained antidepressant effects.",
        full_text=(
            "Background: Major depressive disorder (MDD) is a leading cause of disability worldwide.\n\n"
            "Methods: This randomized waiting list-controlled clinical trial enrolled 24 participants "
            "with moderate-to-severe MDD. Participants received two psilocybin sessions.\n\n"
            "Results: The magnitude of the effect was large (Cohen d = 2.5 at week 1 and 2.6 at week 4). "
            "71% of participants showed a clinically significant response at week 4.\n\n"
            "Conclusions: These findings support further investigation of psilocybin therapy for MDD."
        ),
    )


@pytest.fixture
def sample_chunks(sample_document: Document) -> list[Chunk]:
    from open_synthesis.corpus.chunker import chunk_document
    return chunk_document(sample_document)


@pytest.fixture
def sample_retrieved_chunks(sample_chunks: list[Chunk]) -> list[RetrievedChunk]:
    return [
        RetrievedChunk(chunk=c, score=1.0 - i * 0.1, retrieval_method="test")
        for i, c in enumerate(sample_chunks)
    ]


@pytest.fixture
def default_settings(tmp_path: Path) -> Settings:
    return Settings(vector_store_path=str(tmp_path / "vectorstore"))
