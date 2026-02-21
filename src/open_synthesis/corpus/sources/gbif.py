"""GBIF (Global Biodiversity Information Facility) API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.gbif.org/v1"


class GbifSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "GBIF biodiversity dataset and species occurrence records",
            "auth_required": False,
            "data_type": "biodiversity",
            "rate_limit": "No formal limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/dataset/search",
                params={"q": query, "limit": max_results},
            )
            resp.raise_for_status()
        except Exception:
            return []
        results = resp.json().get("results", [])
        return [self._to_doc(ds) for ds in results]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(f"{_BASE}/dataset/{identifier}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
        except Exception:
            return None
        return self._to_doc(resp.json())

    def _to_doc(self, dataset: dict) -> Document:
        key = dataset.get("key", "")
        contacts = dataset.get("contacts", [])
        authors = [
            f"{c.get('firstName', '')} {c.get('lastName', '')}".strip()
            for c in contacts
            if c.get("lastName")
        ]
        created = dataset.get("created", "")
        year = int(created[:4]) if created and len(created) >= 4 else None
        return Document(
            source_id=f"gbif:{key}",
            source_type="gbif",
            title=dataset.get("title", ""),
            authors=authors[:5],
            year=year,
            abstract=dataset.get("description", ""),
            doi=dataset.get("doi"),
            url=f"https://www.gbif.org/dataset/{key}",
            metadata={
                "type": dataset.get("type", ""),
                "hosting_organization": dataset.get("hostingOrganizationTitle", ""),
                "record_count": dataset.get("recordCount", 0),
            },
        )
