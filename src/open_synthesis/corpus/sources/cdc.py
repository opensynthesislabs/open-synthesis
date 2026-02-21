"""CDC Open Data (Socrata) API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://data.cdc.gov"


class CdcSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "CDC public health datasets via Socrata Open Data API",
            "auth_required": False,
            "data_type": "datasets",
            "rate_limit": "No official limit; throttled without app token",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/api/catalog/v1",
                params={
                    "q": query,
                    "limit": max_results,
                    "only": "datasets",
                },
            )
            if resp.status_code != 200:
                return []
            results = resp.json().get("results", [])
        except Exception:
            return []
        return [self._catalog_to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/resource/{identifier}.json",
                params={"$limit": 100},
            )
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                return None
            rows = resp.json()
        except Exception:
            return None

        # Get metadata for title
        try:
            meta_resp = await http.get(f"{_BASE}/api/views/{identifier}.json")
            meta = meta_resp.json() if meta_resp.status_code == 200 else {}
        except Exception:
            meta = {}

        title = meta.get("name", identifier)
        description = meta.get("description", "")

        return Document(
            source_id=f"cdc:{identifier}",
            source_type="cdc",
            title=title,
            abstract=description,
            full_text=json.dumps(rows[:100], indent=2) if rows else None,
            url=f"{_BASE}/resource/{identifier}",
            metadata={
                "columns": [c.get("name", "") for c in meta.get("columns", [])[:20]],
                "row_count": len(rows),
                "category": meta.get("category", ""),
            },
        )

    def _catalog_to_doc(self, result: dict) -> Document:
        resource = result.get("resource", {})
        dataset_id = resource.get("id", "")
        name = resource.get("name", "")
        description = resource.get("description", "")
        columns = resource.get("columns_name", [])

        return Document(
            source_id=f"cdc:{dataset_id}",
            source_type="cdc",
            title=name,
            abstract=description,
            url=f"{_BASE}/resource/{dataset_id}",
            metadata={
                "columns": columns[:20],
                "update_frequency": resource.get("updatedAt", ""),
            },
        )
