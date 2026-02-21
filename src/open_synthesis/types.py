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


class PaperSection(BaseModel):
    """A single section of a multi-section synthesis paper."""

    title: str
    description: str
    search_queries: list[str] = Field(default_factory=list)
    synthesis: str = ""
    chunks_used: list[RetrievedChunk] = Field(default_factory=list)


class PaperResult(BaseModel):
    """Output of the multi-section paper pipeline."""

    topic: str
    domain: str
    sections: list[PaperSection] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    def to_markdown(self) -> str:
        """Render the paper as a markdown document."""
        lines: list[str] = []
        lines.append(f"# {self.topic}\n")
        for section in self.sections:
            lines.append(f"## {section.title}\n")
            lines.append(section.synthesis)
            lines.append("")

        # Collate all sources
        lines.append("## Sources\n")
        seen: set[str] = set()
        source_num = 0
        for section in self.sections:
            for rc in section.chunks_used:
                meta = rc.chunk.metadata
                key = meta.get("doi") or rc.chunk.document_id
                if key in seen:
                    continue
                seen.add(key)
                source_num += 1
                authors = meta.get("authors", "Unknown")
                year = meta.get("year", "n.d.")
                title = meta.get("title", "Untitled")
                source_type = meta.get("source_type", "")
                lines.append(f"{source_num}. {authors} ({year}). *{title}*. [{source_type}]")
        lines.append("")
        return "\n".join(lines)
