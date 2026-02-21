"""ChromaDB wrapper for vector storage."""

from __future__ import annotations

from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

from open_synthesis.types import Chunk, RetrievedChunk


class VectorStore:
    """Persistent ChromaDB store with sentence-transformer embeddings."""

    def __init__(self, persist_path: str = "./vectorstore", embedding_model: str = "all-MiniLM-L6-v2") -> None:
        self._client = chromadb.PersistentClient(path=str(Path(persist_path).resolve()))
        self._embedder = SentenceTransformer(embedding_model)

    def add_chunks(self, domain: str, chunks: list[Chunk]) -> int:
        """Add chunks to a domain collection. Returns count added."""
        if not chunks:
            return 0
        collection = self._client.get_or_create_collection(domain)
        embeddings = self._embedder.encode([c.text for c in chunks]).tolist()
        collection.add(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[c.metadata for c in chunks],
        )
        return len(chunks)

    def query(self, domain: str, query_text: str, n_results: int = 20) -> list[RetrievedChunk]:
        """Query a domain collection by text similarity."""
        collection = self._client.get_collection(domain)
        query_embedding = self._embedder.encode(query_text).tolist()
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"],
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            chunk = Chunk(
                chunk_id=meta.get("source_id", "") + ":q",
                document_id=meta.get("source_id", ""),
                text=doc,
                index=0,
                metadata=meta,
            )
            # ChromaDB returns L2 distances; convert to similarity score
            score = 1.0 / (1.0 + dist)
            chunks.append(RetrievedChunk(chunk=chunk, score=score, retrieval_method="dense"))
        return chunks

    def list_collections(self) -> list[str]:
        """List all domain collections."""
        return [c.name for c in self._client.list_collections()]

    def collection_count(self, domain: str) -> int:
        """Count chunks in a domain collection."""
        try:
            return self._client.get_collection(domain).count()
        except Exception:
            return 0
