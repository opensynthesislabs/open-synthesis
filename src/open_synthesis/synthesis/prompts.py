"""Prompt template loader."""

from __future__ import annotations

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts"


def load_template(name: str) -> str:
    """Load a prompt template by name (without .txt extension)."""
    path = _PROMPTS_DIR / f"{name}.txt"
    return path.read_text()


def format_template(name: str, **kwargs: str) -> str:
    """Load and format a prompt template with the given variables."""
    template = load_template(name)
    return template.format(**kwargs)


def format_context(chunks: list) -> str:
    """Format retrieved chunks into a context string for the synthesis prompt."""
    parts = []
    for i, rc in enumerate(chunks, 1):
        meta = rc.chunk.metadata
        label = f"{meta.get('authors', 'Unknown')} ({meta.get('year', 'n.d.')})"
        source = meta.get("source_type", "")
        parts.append(
            f"[SOURCE {i}: {label} | {source}]\n{rc.chunk.text}"
        )
    return "\n\n---\n\n".join(parts)
