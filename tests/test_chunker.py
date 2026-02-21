"""Tests for text chunking."""

from __future__ import annotations

from open_synthesis.corpus.chunker import chunk_document
from open_synthesis.types import Document


def test_chunk_document(sample_document: Document):
    chunks = chunk_document(sample_document)
    assert len(chunks) > 0
    # Each chunk inherits document metadata
    for c in chunks:
        assert c.metadata["source_type"] == "test"
        assert c.metadata["doi"] == "10.1001/jamapsychiatry.2020.3285"
        assert "Davis AK" in c.metadata["authors"]
        assert c.document_id == "test:001"


def test_chunk_ids_unique(sample_document: Document):
    chunks = chunk_document(sample_document)
    ids = [c.chunk_id for c in chunks]
    assert len(ids) == len(set(ids))


def test_chunk_abstract_fallback():
    doc = Document(
        source_id="test:002",
        source_type="test",
        title="Test Paper",
        abstract="This is a test abstract that should become a single chunk.",
    )
    chunks = chunk_document(doc)
    assert len(chunks) == 1
    assert "test abstract" in chunks[0].text


def test_chunk_empty_document():
    doc = Document(
        source_id="test:003",
        source_type="test",
        title="Empty Paper",
    )
    chunks = chunk_document(doc)
    assert chunks == []


def test_short_paragraphs_merged():
    doc = Document(
        source_id="test:004",
        source_type="test",
        title="Short Paragraphs",
        full_text="Hi.\n\nBye.\n\nThis is a longer paragraph that should stand on its own and not be merged.",
    )
    chunks = chunk_document(doc, min_chunk_length=50)
    # "Hi." and "Bye." are too short, should be merged
    assert len(chunks) <= 2
