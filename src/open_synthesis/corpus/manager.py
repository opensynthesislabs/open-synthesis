"""Corpus ingestion orchestrator."""

from __future__ import annotations

import asyncio
from typing import Any

from open_synthesis.config import Settings
from open_synthesis.corpus.base import DataSource
from open_synthesis.corpus.chunker import chunk_document
from open_synthesis.corpus.sources import SOURCE_REGISTRY
from open_synthesis.corpus.store import VectorStore
from open_synthesis.types import Document


class CorpusManager:
    """Orchestrates search across data sources, deduplication, chunking, and storage."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VectorStore(
            persist_path=settings.vector_store_path,
            embedding_model=settings.embedding.model,
        )

    async def ingest(
        self,
        query: str,
        domain: str,
        source_names: list[str] | None = None,
        max_results_per_source: int = 20,
    ) -> dict[str, Any]:
        """Search sources, deduplicate, chunk, embed, and store."""
        sources = self._get_sources(source_names)
        all_docs = await self._search_all(sources, query, max_results_per_source)
        deduped = self._deduplicate(all_docs)

        total_chunks = 0
        for doc in deduped:
            chunks = chunk_document(doc)
            total_chunks += self.store.add_chunks(domain, chunks)

        # Close all source clients
        for src in sources:
            await src.close()

        return {"documents": len(deduped), "chunks": total_chunks}

    def _get_sources(self, names: list[str] | None) -> list[DataSource]:
        if names:
            return [SOURCE_REGISTRY[n]() for n in names if n in SOURCE_REGISTRY]
        return [cls() for cls in SOURCE_REGISTRY.values()]

    async def _search_all(
        self,
        sources: list[DataSource],
        query: str,
        max_results: int,
    ) -> list[Document]:
        tasks = [src.search(query, max_results) for src in sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        docs: list[Document] = []
        for result in results:
            if isinstance(result, Exception):
                continue
            docs.extend(result)
        return docs

    def _deduplicate(self, docs: list[Document]) -> list[Document]:
        """Deduplicate by DOI, falling back to source_id."""
        seen: set[str] = set()
        unique: list[Document] = []
        for doc in docs:
            key = doc.doi if doc.doi else doc.source_id
            if key not in seen:
                seen.add(key)
                unique.append(doc)
        return unique
