"""Multi-section paper synthesis pipeline."""

from __future__ import annotations

import asyncio
import re

from rich.console import Console

from open_synthesis.config import Settings
from open_synthesis.corpus.manager import CorpusManager
from open_synthesis.corpus.store import VectorStore
from open_synthesis.retrieval.dense import dense_search
from open_synthesis.retrieval.hybrid import reciprocal_rank_fusion
from open_synthesis.retrieval.reranker import rerank
from open_synthesis.retrieval.sparse import BM25Index
from open_synthesis.synthesis.client import RunPodClient
from open_synthesis.synthesis.prompts import format_context, format_template
from open_synthesis.types import Chunk, PaperResult, PaperSection, RetrievedChunk

console = Console()


class PaperPipeline:
    """Generates multi-section research papers via per-section retrieval and synthesis."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VectorStore(
            persist_path=settings.vector_store_path,
            embedding_model=settings.embedding.model,
        )
        self.runpod = RunPodClient(settings.runpod)
        self.corpus = CorpusManager(settings)

    async def run(
        self,
        topic: str,
        domain: str,
        source_names: list[str] | None = None,
    ) -> PaperResult:
        """Full pipeline: outline → per-section (queries → ingest → retrieve → synthesize) → combine."""
        try:
            # Step 1: Generate outline
            console.print("[bold]Step 1:[/bold] Generating outline...")
            sections = await self._generate_outline(topic)
            console.print(f"  Generated {len(sections)} sections:")
            for i, s in enumerate(sections, 1):
                console.print(f"    {i}. {s.title}")

            # Step 2: Process each section sequentially
            for i, section in enumerate(sections, 1):
                console.print(f"\n[bold]Step 2.{i}:[/bold] Processing section: [cyan]{section.title}[/cyan]")

                # 2a: Generate search queries
                console.print("  Generating search queries...")
                queries = await self._generate_queries(topic, section)
                section.search_queries = queries
                console.print(f"  Queries: {queries}")

                # 2b: Ingest papers for each query
                console.print("  Ingesting papers...")
                for query in queries:
                    await self.corpus.ingest(query, domain, source_names=source_names)

                # 2c: Hybrid retrieval
                console.print("  Retrieving relevant chunks...")
                combined_query = f"{section.title}: {section.description}"
                chunks = self._hybrid_retrieve(combined_query, domain)
                section.chunks_used = chunks
                console.print(f"  Retrieved {len(chunks)} chunks")

                # 2d: Synthesize section
                console.print("  Synthesizing section...")
                synthesis = await self._synthesize_section(topic, section, chunks)
                section.synthesis = synthesis
                word_count = len(synthesis.split())
                console.print(f"  [green]Done[/green] ({word_count} words)")

            # Step 3: Combine
            console.print("\n[bold]Step 3:[/bold] Combining sections...")
            result = PaperResult(topic=topic, domain=domain, sections=sections)
            total_words = sum(len(s.synthesis.split()) for s in sections)
            console.print(f"[bold green]Paper complete.[/bold green] {len(sections)} sections, {total_words} total words.")

            return result
        finally:
            await self.runpod.close()

    async def _generate_outline(self, topic: str) -> list[PaperSection]:
        """Ask the LLM to produce a structured outline."""
        prompt = format_template("outline", topic=topic)
        text = await self.runpod.generate(
            prompt=prompt,
            context="",
            temperature=0.4,
            max_tokens=2048,
        )
        return self._parse_outline(text)

    def _parse_outline(self, text: str) -> list[PaperSection]:
        """Parse SECTION: Title | Description lines from LLM output."""
        sections: list[PaperSection] = []
        for line in text.strip().splitlines():
            line = line.strip()
            match = re.match(r"^SECTION:\s*(.+?)\s*\|\s*(.+)$", line)
            if match:
                sections.append(PaperSection(
                    title=match.group(1).strip(),
                    description=match.group(2).strip(),
                ))
        if not sections:
            raise ValueError(
                f"Failed to parse outline from LLM output. Raw output:\n{text}"
            )
        return sections

    async def _generate_queries(self, topic: str, section: PaperSection) -> list[str]:
        """Ask the LLM to generate search queries for a section."""
        prompt = format_template(
            "section_queries",
            topic=topic,
            section_title=section.title,
            section_description=section.description,
        )
        text = await self.runpod.generate(
            prompt=prompt,
            context="",
            temperature=0.3,
            max_tokens=512,
        )
        queries = [q.strip() for q in text.strip().splitlines() if q.strip()]
        return queries[:3]  # Cap at 3 queries

    def _hybrid_retrieve(self, question: str, domain: str) -> list[RetrievedChunk]:
        """Hybrid retrieval — same logic as SynthesisPipeline."""
        n = self.settings.retrieval.n_results
        dense_results = dense_search(self.store, domain, question, n_results=n)
        all_chunks: list[Chunk] = [rc.chunk for rc in dense_results]
        if all_chunks:
            bm25 = BM25Index(all_chunks)
            sparse_results = bm25.search(question, n_results=n)
        else:
            sparse_results = []
        fused = reciprocal_rank_fusion(
            [dense_results, sparse_results],
            weights=[self.settings.retrieval.dense_weight, self.settings.retrieval.sparse_weight],
            n_results=n,
        )
        return rerank(question, fused, n_results=n)

    async def _synthesize_section(
        self,
        topic: str,
        section: PaperSection,
        chunks: list[RetrievedChunk],
    ) -> str:
        """Synthesize a single section using retrieved chunks as context."""
        context = format_context(chunks)
        prompt = format_template(
            "section_synthesis",
            topic=topic,
            section_title=section.title,
            section_description=section.description,
        )
        return await self.runpod.generate(
            prompt=prompt,
            context=context,
            temperature=self.settings.inference.temperature,
            max_tokens=self.settings.inference.max_new_tokens,
        )
