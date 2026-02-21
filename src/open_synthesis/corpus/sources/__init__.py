"""Data source registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_synthesis.corpus.base import DataSource

def _registry() -> dict[str, type[DataSource]]:
    from open_synthesis.corpus.sources.arxiv import ArxivSource
    from open_synthesis.corpus.sources.census import CensusSource
    from open_synthesis.corpus.sources.clinicaltrials import ClinicalTrialsSource
    from open_synthesis.corpus.sources.core_api import CoreSource
    from open_synthesis.corpus.sources.crossref import CrossrefSource
    from open_synthesis.corpus.sources.datagov import DataGovSource
    from open_synthesis.corpus.sources.fred import FredSource
    from open_synthesis.corpus.sources.oecd import OecdSource
    from open_synthesis.corpus.sources.openalex import OpenAlexSource
    from open_synthesis.corpus.sources.pubmed import PubMedSource
    from open_synthesis.corpus.sources.semantic_scholar import SemanticScholarSource

    return {
        "semantic_scholar": SemanticScholarSource,
        "pubmed": PubMedSource,
        "arxiv": ArxivSource,
        "crossref": CrossrefSource,
        "core": CoreSource,
        "openalex": OpenAlexSource,
        "census": CensusSource,
        "fred": FredSource,
        "clinicaltrials": ClinicalTrialsSource,
        "oecd": OecdSource,
        "datagov": DataGovSource,
    }

SOURCE_REGISTRY: dict[str, type[DataSource]] = _registry()
