"""Open Targets Platform API (GraphQL) integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.platform.opentargets.org/api/v4/graphql"

_SEARCH_QUERY = """
query SearchQuery($q: String!, $size: Int!) {
  search(queryString: $q, entityNames: ["target", "disease", "drug"], page: {index: 0, size: $size}) {
    total
    hits {
      id
      name
      entity
      description
    }
  }
}
"""

_TARGET_QUERY = """
query TargetQuery($id: String!) {
  target(ensemblId: $id) {
    id
    approvedSymbol
    approvedName
    biotype
    functionDescriptions
  }
}
"""

_DISEASE_QUERY = """
query DiseaseQuery($id: String!) {
  disease(efoId: $id) {
    id
    name
    description
    therapeuticAreas { id name }
  }
}
"""

_DRUG_QUERY = """
query DrugQuery($id: String!) {
  drug(chemblId: $id) {
    id
    name
    drugType
    description
    maximumClinicalTrialPhase
  }
}
"""


class OpenTargetsSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Target-disease-drug associations from Open Targets Platform",
            "auth_required": False,
            "data_type": "biomedical",
            "rate_limit": "No published limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        resp = await http.post(
            _BASE,
            json={
                "query": _SEARCH_QUERY,
                "variables": {"q": query, "size": max_results},
            },
        )
        if resp.status_code != 200:
            return []
        hits = (
            resp.json()
            .get("data", {})
            .get("search", {})
            .get("hits", [])
        )
        return [self._hit_to_doc(h) for h in hits]

    async def fetch(self, identifier: str) -> Document | None:
        entity_type, entity_queries = self._detect_entity(identifier)
        if not entity_queries:
            return None
        http = await self.client()
        resp = await http.post(
            _BASE,
            json={
                "query": entity_queries,
                "variables": {"id": identifier},
            },
        )
        if resp.status_code != 200:
            return None
        data = resp.json().get("data", {})
        entity = data.get(entity_type)
        if not entity:
            return None
        return Document(
            source_id=f"opentargets:{entity.get('id', identifier)}",
            source_type="open_targets",
            title=entity.get("name") or entity.get("approvedName") or entity.get("approvedSymbol") or identifier,
            abstract=entity.get("description", "")
            if isinstance(entity.get("description"), str)
            else "; ".join(entity.get("functionDescriptions", [])[:3]),
            metadata={"entity_type": entity_type, **{k: v for k, v in entity.items() if k not in ("description", "functionDescriptions")}},
        )

    def _detect_entity(self, identifier: str) -> tuple[str, str | None]:
        if identifier.startswith("ENSG"):
            return "target", _TARGET_QUERY
        if identifier.startswith("EFO_") or identifier.startswith("MONDO_"):
            return "disease", _DISEASE_QUERY
        if identifier.startswith("CHEMBL"):
            return "drug", _DRUG_QUERY
        return "", None

    def _hit_to_doc(self, hit: dict) -> Document:
        return Document(
            source_id=f"opentargets:{hit.get('id', '')}",
            source_type="open_targets",
            title=hit.get("name", ""),
            abstract=hit.get("description", ""),
            metadata={"entity": hit.get("entity", ""), "entity_id": hit.get("id", "")},
        )
