"""U.S. Census Bureau API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.census.gov/data"


class CensusSource(DataSource):
    """American Community Survey and decennial census data."""

    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "U.S. Census Bureau ACS/decennial data",
            "auth_required": True,
            "data_type": "statistics",
            "rate_limit": "500 requests/day with free API key",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        """Search census datasets.

        For census, 'query' is treated as a dataset path like '2022/acs/acs5'
        and variables like 'B01001_001E' (total population).
        Format: "YEAR/DATASET?get=VARS&for=GEOGRAPHY"
        Example: "2022/acs/acs5?get=B01001_001E,NAME&for=state:*"
        """
        if "?" not in query:
            # If plain text query, search the dataset catalog
            return await self._search_catalog(query, max_results)

        path, params_str = query.split("?", 1)
        params: dict[str, str] = {}
        for part in params_str.split("&"):
            k, v = part.split("=", 1)
            params[k] = v
        if self.api_key:
            params["key"] = self.api_key

        http = await self.client()
        resp = await http.get(f"{_BASE}/{path}", params=params)
        resp.raise_for_status()
        data = resp.json()

        if not data or len(data) < 2:
            return []

        headers = data[0]
        text = json.dumps({"headers": headers, "rows": data[1:max_results + 1]}, indent=2)
        return [Document(
            source_id=f"census:{path}",
            source_type="census",
            title=f"Census data: {path}",
            full_text=text,
            metadata={"variables": params.get("get", ""), "geography": params.get("for", "")},
        )]

    async def _search_catalog(self, query: str, max_results: int) -> list[Document]:
        http = await self.client()
        resp = await http.get(f"{_BASE}.json")
        resp.raise_for_status()
        datasets = resp.json().get("dataset", [])
        query_lower = query.lower()
        matched = [
            d for d in datasets
            if query_lower in d.get("title", "").lower()
            or query_lower in d.get("description", "").lower()
        ][:max_results]
        return [
            Document(
                source_id=f"census:catalog:{d.get('c_dataset', [''])[0]}",
                source_type="census",
                title=d.get("title", ""),
                abstract=d.get("description", ""),
                url=d.get("distribution", [{}])[0].get("accessURL", ""),
            )
            for d in matched
        ]

    async def fetch(self, identifier: str) -> Document | None:
        results = await self.search(identifier, max_results=1)
        return results[0] if results else None
