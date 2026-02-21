"""Data source registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from open_synthesis.corpus.base import DataSource

def _registry() -> dict[str, type[DataSource]]:
    from open_synthesis.corpus.sources.arxiv import ArxivSource
    from open_synthesis.corpus.sources.biorxiv import BiorxivSource
    from open_synthesis.corpus.sources.cdc import CdcSource
    from open_synthesis.corpus.sources.census import CensusSource
    from open_synthesis.corpus.sources.chembl import ChemblSource
    from open_synthesis.corpus.sources.clinicaltrials import ClinicalTrialsSource
    from open_synthesis.corpus.sources.core_api import CoreSource
    from open_synthesis.corpus.sources.crossref import CrossrefSource
    from open_synthesis.corpus.sources.datagov import DataGovSource
    from open_synthesis.corpus.sources.europe_pmc import EuropePmcSource
    from open_synthesis.corpus.sources.eurostat import EurostatSource
    from open_synthesis.corpus.sources.fred import FredSource
    from open_synthesis.corpus.sources.gbif import GbifSource
    from open_synthesis.corpus.sources.imf import ImfSource
    from open_synthesis.corpus.sources.gwas_catalog import GwasCatalogSource
    from open_synthesis.corpus.sources.ncbi import NcbiGeneSource
    from open_synthesis.corpus.sources.oecd import OecdSource
    from open_synthesis.corpus.sources.openaire import OpenAireSource
    from open_synthesis.corpus.sources.openalex import OpenAlexSource
    from open_synthesis.corpus.sources.opencitations import OpenCitationsSource
    from open_synthesis.corpus.sources.open_targets import OpenTargetsSource
    from open_synthesis.corpus.sources.openfda import OpenFdaSource
    from open_synthesis.corpus.sources.osf_preprints import OsfPreprintsSource
    from open_synthesis.corpus.sources.pubchem import PubChemSource
    from open_synthesis.corpus.sources.pubmed import PubMedSource
    from open_synthesis.corpus.sources.semantic_scholar import SemanticScholarSource
    from open_synthesis.corpus.sources.springer import SpringerSource
    from open_synthesis.corpus.sources.un_sdg import UnSdgSource
    from open_synthesis.corpus.sources.unpaywall import UnpaywallSource
    from open_synthesis.corpus.sources.who_gho import WhoGhoSource
    from open_synthesis.corpus.sources.world_bank import WorldBankSource

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
        "biorxiv": BiorxivSource,
        "europe_pmc": EuropePmcSource,
        "unpaywall": UnpaywallSource,
        "world_bank": WorldBankSource,
        "who_gho": WhoGhoSource,
        "openfda": OpenFdaSource,
        "cdc": CdcSource,
        "pubchem": PubChemSource,
        "osf_preprints": OsfPreprintsSource,
        "eurostat": EurostatSource,
        "ncbi_gene": NcbiGeneSource,
        "gwas_catalog": GwasCatalogSource,
        "un_sdg": UnSdgSource,
        "gbif": GbifSource,
        "openaire": OpenAireSource,
        "imf": ImfSource,
        "springer": SpringerSource,
        "opencitations": OpenCitationsSource,
        "chembl": ChemblSource,
        "open_targets": OpenTargetsSource,
    }

SOURCE_REGISTRY: dict[str, type[DataSource]] = _registry()
