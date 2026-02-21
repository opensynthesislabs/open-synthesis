"""Shared domain models."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ConfidenceLevel(str, Enum):
    WELL_SUPPORTED = "well_supported"
    LIMITED = "limited"
    CONTESTED = "contested"
    INSUFFICIENT = "insufficient"


class Document(BaseModel):
    """A source document retrieved from a data source."""

    source_id: str
    source_type: str  # e.g. "semantic_scholar", "pubmed"
    title: str
    authors: list[str] = Field(default_factory=list)
    year: int | None = None
    doi: str | None = None
    abstract: str | None = None
    full_text: str | None = None
    url: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Chunk(BaseModel):
    """A paragraph-level chunk derived from a Document."""

    chunk_id: str
    document_id: str
    text: str
    index: int  # position within the document
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievedChunk(BaseModel):
    """A chunk returned by the retrieval layer with relevance score."""

    chunk: Chunk
    score: float
    retrieval_method: str  # "dense", "sparse", "hybrid"


class SynthesisResult(BaseModel):
    """Output of the synthesis pipeline."""

    question: str
    domain: str
    synthesis: str
    chunks_used: list[RetrievedChunk] = Field(default_factory=list)
    confidence: ConfidenceLevel | None = None
    citation_check: dict[str, Any] | None = None
    hallucination_flags: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
