"""Hallucination detection via second LLM pass."""

from __future__ import annotations

import json
from typing import Any


def check_hallucinations(llm_output: dict[str, Any] | str) -> list[str]:
    """Parse hallucination check LLM output into a list of flag descriptions.

    Expected LLM output is a JSON object with:
    - flags: list of {type, text, explanation}
    - clean: boolean
    """
    if isinstance(llm_output, str):
        text = llm_output
    elif isinstance(llm_output, dict):
        text = llm_output.get("synthesis", str(llm_output))
    else:
        return [f"Unparseable hallucination check output: {llm_output}"]

    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return [f"Unparseable hallucination check output: {text[:200]}"]

    if parsed.get("clean", False):
        return []

    flags = []
    for flag in parsed.get("flags", []):
        flag_type = flag.get("type", "unknown")
        flag_text = flag.get("text", "")
        explanation = flag.get("explanation", "")
        flags.append(f"[{flag_type}] {flag_text}: {explanation}")

    return flags
