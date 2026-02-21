"""Tests for validation modules."""

from __future__ import annotations

import json

from open_synthesis.types import ConfidenceLevel
from open_synthesis.validation.citation import check_citations
from open_synthesis.validation.hallucination import check_hallucinations
from open_synthesis.validation.uncertainty import assess_uncertainty


# --- Citation checks ---

def test_citation_check_valid_json():
    output = json.dumps({
        "valid": [1, 2, 3],
        "invalid": [],
        "uncited_claims": ["Some claim"],
    })
    result = check_citations(output)
    assert result["valid"] == [1, 2, 3]
    assert result["invalid"] == []
    assert result["uncited_claims"] == ["Some claim"]
    assert result["parse_error"] is False


def test_citation_check_invalid_json():
    result = check_citations("not json at all")
    assert result["parse_error"] is True


def test_citation_check_dict_input():
    output = {"synthesis": json.dumps({"valid": [1], "invalid": [], "uncited_claims": []})}
    result = check_citations(output)
    assert result["valid"] == [1]


# --- Hallucination checks ---

def test_hallucination_clean():
    output = json.dumps({"clean": True, "flags": []})
    assert check_hallucinations(output) == []


def test_hallucination_flags():
    output = json.dumps({
        "clean": False,
        "flags": [
            {"type": "fabricated_stat", "text": "95% efficacy", "explanation": "Not in sources"},
        ],
    })
    flags = check_hallucinations(output)
    assert len(flags) == 1
    assert "fabricated_stat" in flags[0]


def test_hallucination_unparseable():
    flags = check_hallucinations("garbage")
    assert len(flags) == 1
    assert "Unparseable" in flags[0]


# --- Uncertainty ---

def test_uncertainty_well_supported():
    output = json.dumps({"confidence": "well_supported", "reasoning": "...", "key_gaps": []})
    assert assess_uncertainty(output) == ConfidenceLevel.WELL_SUPPORTED


def test_uncertainty_contested():
    output = json.dumps({"confidence": "contested", "reasoning": "...", "key_gaps": ["replication"]})
    assert assess_uncertainty(output) == ConfidenceLevel.CONTESTED


def test_uncertainty_fallback():
    assert assess_uncertainty("not json") == ConfidenceLevel.INSUFFICIENT
