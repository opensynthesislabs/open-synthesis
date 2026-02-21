"""Tests for config loading."""

from __future__ import annotations

from pathlib import Path

from open_synthesis.config import Settings, load_settings


def test_default_settings():
    s = Settings()
    assert s.vector_store_path == "./vectorstore"
    assert s.embedding.model == "all-MiniLM-L6-v2"
    assert s.inference.temperature == 0.3
    assert s.retrieval.n_results == 20


def test_load_from_toml(tmp_path: Path):
    toml = tmp_path / "test.toml"
    toml.write_text(
        '[inference]\ntemperature = 0.7\n\n[retrieval]\nn_results = 10\n'
    )
    s = load_settings(toml)
    assert s.inference.temperature == 0.7
    assert s.retrieval.n_results == 10
    # Other settings keep defaults
    assert s.embedding.model == "all-MiniLM-L6-v2"


def test_load_missing_file():
    s = load_settings(Path("/nonexistent/config.toml"))
    assert s.vector_store_path == "./vectorstore"


def test_env_override(monkeypatch: object, tmp_path: Path):
    import os
    os.environ["RUNPOD_POD_ID"] = "test-pod"
    try:
        s = Settings(runpod=__import__("open_synthesis.config", fromlist=["RunPodSettings"]).RunPodSettings())
        assert s.runpod.pod_id == "test-pod"
    finally:
        os.environ.pop("RUNPOD_POD_ID", None)
