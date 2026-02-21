"""Citation verification via second LLM pass."""

from __future__ import annotations

import json
from typing import Any


def check_citations(llm_output: dict[str, Any] | str) -> dict[str, Any]:
    """Parse citation check LLM output into structured result.

    Expected LLM output is a JSON object with:
    - valid: list of citation numbers
    - invalid: list of {citation, claim, issue}
    - uncited_claims: list of strings
    """
    if isinstance(llm_output, str):
        try:
            parsed = json.loads(llm_output)
        except json.JSONDecodeError:
            return {"raw": llm_output, "parse_error": True}
    elif isinstance(llm_output, dict):
        text = llm_output.get("synthesis", str(llm_output))
        try:
            parsed = json.loads(text)
        except (json.JSONDecodeError, TypeError):
            return {"raw": text, "parse_error": True}
    else:
        return {"raw": str(llm_output), "parse_error": True}

    return {
        "valid": parsed.get("valid", []),
        "invalid": parsed.get("invalid", []),
        "uncited_claims": parsed.get("uncited_claims", []),
        "parse_error": False,
    }
