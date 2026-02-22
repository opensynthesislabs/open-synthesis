"""Tests for the FastAPI research chat server."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from open_synthesis.config import Settings
from open_synthesis.types import Chunk, RetrievedChunk


@pytest.fixture
def settings(tmp_path):
    return Settings(vector_store_path=str(tmp_path / "vectorstore"))


@pytest.fixture
def mock_chunks():
    chunk = Chunk(
        chunk_id="test:001:0",
        document_id="test:001",
        text="Psilocybin showed antidepressant effects.",
        index=0,
        metadata={
            "authors": "Davis AK et al.",
            "year": "2021",
            "title": "Effects of Psilocybin on MDD",
            "source_type": "semantic_scholar",
        },
    )
    return [RetrievedChunk(chunk=chunk, score=0.95, retrieval_method="hybrid")]


@pytest.fixture
def app(settings, mock_chunks):
    from open_synthesis.server import create_app

    application = create_app(settings, origins=["*"])

    # Directly set app state (bypassing lifespan for tests)
    mock_store = MagicMock()
    mock_store.list_collections.return_value = ["default", "psychedelic-therapy"]
    mock_runpod = AsyncMock()
    mock_runpod.generate = AsyncMock(return_value="Synthesis result text.")
    mock_runpod.close = AsyncMock()

    import asyncio
    application.state.settings = settings
    application.state.store = mock_store
    application.state.runpod = mock_runpod
    application.state.semaphore = asyncio.Semaphore(1)

    return application


@pytest.fixture
def client(app):
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health(client):
    async with client:
        resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "default" in data["domains"]


@pytest.mark.asyncio
async def test_domains(client):
    async with client:
        resp = await client.get("/api/domains")
    assert resp.status_code == 200
    domains = resp.json()
    assert "default" in domains
    assert "psychedelic-therapy" in domains


@pytest.mark.asyncio
async def test_chat(client, mock_chunks):
    with patch("open_synthesis.server._hybrid_retrieve", return_value=mock_chunks):
        async with client:
            resp = await client.post(
                "/api/chat",
                json={"question": "What are the effects of psilocybin?", "domain": "default"},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["question"] == "What are the effects of psilocybin?"
    assert "synthesis" in data


@pytest.mark.asyncio
async def test_chat_stream(client, app, mock_chunks):
    async def mock_stream(*args, **kwargs):
        for token in ["Hello", " world", "!"]:
            yield token

    app.state.runpod.generate_stream = mock_stream

    with patch("open_synthesis.server._hybrid_retrieve", return_value=mock_chunks):
        async with client:
            resp = await client.post(
                "/api/chat/stream",
                json={"question": "Test question", "domain": "default"},
            )
    assert resp.status_code == 200
    body = resp.text
    assert "event: sources" in body
    assert "event: chunk" in body
    assert "event: done" in body


@pytest.mark.asyncio
async def test_cors_preflight(client):
    async with client:
        resp = await client.options(
            "/api/health",
            headers={
                "Origin": "https://opensynthesis.dev",
                "Access-Control-Request-Method": "GET",
            },
        )
    # With origins=["*"], CORS middleware should allow
    assert resp.status_code in (200, 204)


@pytest.mark.asyncio
async def test_chat_missing_domain(client):
    with patch(
        "open_synthesis.server._hybrid_retrieve",
        side_effect=Exception("Collection not found"),
    ):
        async with client:
            resp = await client.post(
                "/api/chat",
                json={"question": "Test", "domain": "nonexistent"},
            )
    assert resp.status_code == 404
