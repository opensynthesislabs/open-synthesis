"""Uncertainty quantification via second LLM pass."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.types import ConfidenceLevel

_LEVEL_MAP = {
    "well_supported": ConfidenceLevel.WELL_SUPPORTED,
    "limited": ConfidenceLevel.LIMITED,
    "contested": ConfidenceLevel.CONTESTED,
    "insufficient": ConfidenceLevel.INSUFFICIENT,
}


def assess_uncertainty(llm_output: dict[str, Any] | str) -> ConfidenceLevel:
    """Parse uncertainty assessment LLM output into a ConfidenceLevel.

    Expected LLM output is a JSON object with:
    - confidence: one of "well_supported", "limited", "contested", "insufficient"
    - reasoning: string
    - key_gaps: list of strings
    """
    if isinstance(llm_output, str):
        text = llm_output
    elif isinstance(llm_output, dict):
        text = llm_output.get("synthesis", str(llm_output))
    else:
        return ConfidenceLevel.INSUFFICIENT

    try:
        parsed = json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return ConfidenceLevel.INSUFFICIENT

    level_str = parsed.get("confidence", "insufficient").lower()
    return _LEVEL_MAP.get(level_str, ConfidenceLevel.INSUFFICIENT)
