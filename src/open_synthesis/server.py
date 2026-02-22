"""FastAPI server wrapping the RAG synthesis pipeline."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from open_synthesis.config import Settings
from open_synthesis.corpus.store import VectorStore
from open_synthesis.retrieval.dense import dense_search
from open_synthesis.retrieval.hybrid import reciprocal_rank_fusion
from open_synthesis.retrieval.reranker import rerank
from open_synthesis.retrieval.sparse import BM25Index
from open_synthesis.synthesis.client import RunPodClient
from open_synthesis.synthesis.prompts import format_context, format_template
from open_synthesis.types import RetrievedChunk, SynthesisResult

logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    question: str
    domain: str = "default"
    run_validation: bool = False


class HealthResponse(BaseModel):
    status: str
    vllm_url: str
    domains: list[str]


def _hybrid_retrieve(
    store: VectorStore, settings: Settings, question: str, domain: str,
) -> list[RetrievedChunk]:
    """Run the hybrid retrieval pipeline (dense + BM25 + fusion + rerank)."""
    n = settings.retrieval.n_results
    dense_results = dense_search(store, domain, question, n_results=n)
    all_chunks = [rc.chunk for rc in dense_results]
    if all_chunks:
        bm25 = BM25Index(all_chunks)
        sparse_results = bm25.search(question, n_results=n)
    else:
        sparse_results = []
    fused = reciprocal_rank_fusion(
        [dense_results, sparse_results],
        weights=[settings.retrieval.dense_weight, settings.retrieval.sparse_weight],
        n_results=n,
    )
    return rerank(question, fused, n_results=n)


def create_app(settings: Settings, origins: list[str] | None = None) -> FastAPI:
    """Create and configure the FastAPI application."""

    gpu_semaphore = asyncio.Semaphore(1)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        # Startup: store pipeline components in app state
        app.state.settings = settings
        app.state.store = VectorStore(
            persist_path=settings.vector_store_path,
            embedding_model=settings.embedding.model,
        )
        app.state.runpod = RunPodClient(settings.runpod)
        app.state.semaphore = gpu_semaphore
        logger.info("Server started — vLLM target: %s", settings.runpod.base_url or "pod proxy")
        yield
        # Shutdown
        await app.state.runpod.close()
        logger.info("Server stopped")

    app = FastAPI(
        title="Open Synthesis API",
        version="0.1.0",
        lifespan=lifespan,
    )

    allowed_origins = origins or [
        "https://opensynthesis.dev",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "null",  # file:// protocol sends Origin: null
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    async def health(request: Request) -> HealthResponse:
        store: VectorStore = request.app.state.store
        s: Settings = request.app.state.settings
        domains = store.list_collections()
        vllm_url = s.runpod.base_url or f"https://{s.runpod.pod_id}-8000.proxy.runpod.net"
        return HealthResponse(status="ok", vllm_url=vllm_url, domains=domains)

    @app.get("/api/domains")
    async def domains(request: Request) -> list[str]:
        store: VectorStore = request.app.state.store
        return store.list_collections()

    @app.post("/api/chat")
    async def chat(body: ChatRequest, request: Request) -> dict:
        sem: asyncio.Semaphore = request.app.state.semaphore
        if not sem._value:
            raise HTTPException(429, "Server busy — another request is in progress")
        async with sem:
            return await _do_chat(body, request)

    async def _do_chat(body: ChatRequest, request: Request) -> dict:
        store: VectorStore = request.app.state.store
        s: Settings = request.app.state.settings
        runpod: RunPodClient = request.app.state.runpod

        try:
            chunks = _hybrid_retrieve(store, s, body.question, body.domain)
        except Exception as exc:
            raise HTTPException(404, f"Domain '{body.domain}' not found or empty: {exc}")

        context = format_context(chunks)
        prompt = format_template("synthesis", question=body.question)
        text = await runpod.generate(
            prompt=prompt,
            context=context,
            temperature=s.inference.temperature,
            max_tokens=s.inference.max_new_tokens,
        )

        result = SynthesisResult(
            question=body.question,
            domain=body.domain,
            synthesis=text,
            chunks_used=chunks,
        )
        return result.model_dump(mode="json")

    @app.post("/api/chat/stream")
    async def chat_stream(body: ChatRequest, request: Request) -> EventSourceResponse:
        sem: asyncio.Semaphore = request.app.state.semaphore
        if not sem._value:
            raise HTTPException(429, "Server busy — another request is in progress")

        async def event_generator() -> AsyncIterator[dict]:
            async with sem:
                store: VectorStore = request.app.state.store
                s: Settings = request.app.state.settings
                runpod: RunPodClient = request.app.state.runpod

                # Retrieval phase
                try:
                    chunks = _hybrid_retrieve(store, s, body.question, body.domain)
                except Exception as exc:
                    yield {"event": "error", "data": f"Domain '{body.domain}' not found: {exc}"}
                    return

                # Send sources
                sources = []
                for rc in chunks:
                    meta = rc.chunk.metadata
                    sources.append({
                        "authors": meta.get("authors", "Unknown"),
                        "year": meta.get("year", "n.d."),
                        "title": meta.get("title", "Untitled"),
                        "source_type": meta.get("source_type", ""),
                        "score": round(rc.score, 3),
                    })
                import json
                yield {"event": "sources", "data": json.dumps(sources)}

                # Streaming synthesis
                context = format_context(chunks)
                prompt = format_template("synthesis", question=body.question)
                try:
                    async for token in runpod.generate_stream(
                        prompt=prompt,
                        context=context,
                        temperature=s.inference.temperature,
                        max_tokens=s.inference.max_new_tokens,
                    ):
                        yield {"event": "chunk", "data": token}
                except Exception as exc:
                    yield {"event": "error", "data": str(exc)}
                    return

                yield {"event": "done", "data": ""}

        return EventSourceResponse(event_generator())

    return app
