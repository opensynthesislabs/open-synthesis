"""End-to-end synthesis pipeline."""

from __future__ import annotations

from open_synthesis.config import Settings
from open_synthesis.corpus.store import VectorStore
from open_synthesis.retrieval.dense import dense_search
from open_synthesis.retrieval.hybrid import reciprocal_rank_fusion
from open_synthesis.retrieval.reranker import rerank
from open_synthesis.retrieval.sparse import BM25Index
from open_synthesis.synthesis.client import RunPodClient
from open_synthesis.synthesis.prompts import format_context, format_template
from open_synthesis.types import Chunk, ConfidenceLevel, RetrievedChunk, SynthesisResult
from open_synthesis.validation.citation import check_citations
from open_synthesis.validation.hallucination import check_hallucinations
from open_synthesis.validation.uncertainty import assess_uncertainty


class SynthesisPipeline:
    """Orchestrates: retrieval → context formatting → RunPod inference → validation."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.store = VectorStore(
            persist_path=settings.vector_store_path,
            embedding_model=settings.embedding.model,
        )
        self.runpod = RunPodClient(settings.runpod)

    async def run(
        self,
        question: str,
        domain: str,
        validate: bool = True,
    ) -> SynthesisResult:
        """Full pipeline: retrieve → synthesize → optionally validate."""
        # Retrieve
        chunks = self._hybrid_retrieve(question, domain)

        # Format context and prompt
        context = format_context(chunks)
        prompt = format_template("synthesis", question=question)

        # Call RunPod
        output = await self.runpod.runsync({
            "prompt": prompt,
            "context": context,
            "temperature": self.settings.inference.temperature,
            "max_new_tokens": self.settings.inference.max_new_tokens,
        })

        result = SynthesisResult(
            question=question,
            domain=domain,
            synthesis=output.get("synthesis", str(output)),
            chunks_used=chunks,
        )

        if validate:
            result = await self.validate_result(result)

        return result

    def _hybrid_retrieve(self, question: str, domain: str) -> list[RetrievedChunk]:
        n = self.settings.retrieval.n_results

        # Dense retrieval from ChromaDB
        dense_results = dense_search(self.store, domain, question, n_results=n)

        # Build BM25 index from dense results for sparse re-scoring
        all_chunks: list[Chunk] = [rc.chunk for rc in dense_results]
        if all_chunks:
            bm25 = BM25Index(all_chunks)
            sparse_results = bm25.search(question, n_results=n)
        else:
            sparse_results = []

        # Fuse
        fused = reciprocal_rank_fusion(
            [dense_results, sparse_results],
            weights=[self.settings.retrieval.dense_weight, self.settings.retrieval.sparse_weight],
            n_results=n,
        )

        # Rerank
        return rerank(question, fused, n_results=n)

    async def validate_result(self, result: SynthesisResult) -> SynthesisResult:
        """Run validation passes on a synthesis result."""
        cfg = self.settings.validation

        if cfg.citation_check:
            citation_prompt = format_template(
                "citation_check",
                synthesis=result.synthesis,
                sources=format_context(result.chunks_used),
            )
            citation_output = await self.runpod.runsync({
                "prompt": citation_prompt,
                "context": "",
                "temperature": 0.1,
                "max_new_tokens": 2048,
            })
            result.citation_check = citation_output

        if cfg.hallucination_check:
            hallucination_prompt = format_template(
                "hallucination_check",
                synthesis=result.synthesis,
                sources=format_context(result.chunks_used),
            )
            hallucination_output = await self.runpod.runsync({
                "prompt": hallucination_prompt,
                "context": "",
                "temperature": 0.1,
                "max_new_tokens": 2048,
            })
            flags = check_hallucinations(hallucination_output)
            result.hallucination_flags = flags

        if cfg.uncertainty_quantification:
            uncertainty_prompt = format_template(
                "uncertainty",
                synthesis=result.synthesis,
                sources=format_context(result.chunks_used),
            )
            uncertainty_output = await self.runpod.runsync({
                "prompt": uncertainty_prompt,
                "context": "",
                "temperature": 0.1,
                "max_new_tokens": 1024,
            })
            result.confidence = assess_uncertainty(uncertainty_output)

        return result
