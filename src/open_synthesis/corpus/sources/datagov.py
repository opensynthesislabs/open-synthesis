"""data.gov CKAN catalog integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://catalog.data.gov/api/3"


class DataGovSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "U.S. federal open data catalog via data.gov CKAN API",
            "auth_required": False,
            "data_type": "datasets",
            "rate_limit": "No official limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/action/package_search",
            params={"q": query, "rows": max_results},
        )
        resp.raise_for_status()
        results = resp.json().get("result", {}).get("results", [])
        return [self._to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/action/package_show",
            params={"id": identifier},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        result = resp.json().get("result")
        if not result:
            return None
        return self._to_doc(result)

    def _to_doc(self, pkg: dict) -> Document:
        resources = pkg.get("resources", [])
        urls = [r.get("url", "") for r in resources[:5]]
        return Document(
            source_id=f"datagov:{pkg.get('id', '')}",
            source_type="datagov",
            title=pkg.get("title", ""),
            abstract=pkg.get("notes", ""),
            url=urls[0] if urls else None,
            metadata={
                "organization": pkg.get("organization", {}).get("title", ""),
                "formats": [r.get("format", "") for r in resources[:5]],
                "resource_urls": urls,
            },
        )
