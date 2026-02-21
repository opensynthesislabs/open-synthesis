"""Pydantic settings with TOML config loader."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_CONFIG = Path(__file__).resolve().parent.parent.parent / "config" / "default.toml"


def _load_toml(path: Path) -> dict[str, Any]:
    if path.exists():
        with open(path, "rb") as f:
            return tomllib.load(f)
    return {}


class EmbeddingSettings(BaseSettings):
    model: str = "all-MiniLM-L6-v2"


class RetrievalSettings(BaseSettings):
    n_results: int = 20
    dense_weight: float = 0.6
    sparse_weight: float = 0.4


class InferenceSettings(BaseSettings):
    temperature: float = 0.3
    top_p: float = 0.9
    repetition_penalty: float = 1.1
    max_new_tokens: int = 16384


class RunPodSettings(BaseSettings):
    pod_id: str = ""
    api_key: str = ""
    model: str = "opensynthesis/Qwen3-14B-heretic"
    base_url: str = ""
    timeout: int = 300

    model_config = SettingsConfigDict(env_prefix="RUNPOD_")


class ValidationSettings(BaseSettings):
    citation_check: bool = True
    hallucination_check: bool = True
    uncertainty_quantification: bool = True
    human_review_required: bool = True


class Settings(BaseSettings):
    vector_store_path: str = "./vectorstore"
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)
    inference: InferenceSettings = Field(default_factory=InferenceSettings)
    runpod: RunPodSettings = Field(default_factory=RunPodSettings)
    validation: ValidationSettings = Field(default_factory=ValidationSettings)

    model_config = SettingsConfigDict(env_prefix="OSYN_")


def load_settings(config_path: Path | None = None) -> Settings:
    """Load settings from TOML file, with env var overrides."""
    path = config_path or _DEFAULT_CONFIG
    data = _load_toml(path)

    kwargs: dict[str, Any] = {}
    section_classes = {
        "embedding": EmbeddingSettings,
        "retrieval": RetrievalSettings,
        "inference": InferenceSettings,
        "runpod": RunPodSettings,
        "validation": ValidationSettings,
    }
    for section, cls in section_classes.items():
        toml_vals = data.get(section, {})
        # Remove TOML keys that have env var overrides, so Pydantic
        # picks up the env var instead (explicit kwargs beat env vars).
        prefix = cls.model_config.get("env_prefix", "") or ""
        if prefix:
            toml_vals = {
                k: v for k, v in toml_vals.items()
                if f"{prefix}{k}".upper() not in os.environ
            }
        kwargs[section] = cls(**toml_vals)

    if "vector_store_path" in data:
        kwargs["vector_store_path"] = data["vector_store_path"]

    return Settings(**kwargs)
