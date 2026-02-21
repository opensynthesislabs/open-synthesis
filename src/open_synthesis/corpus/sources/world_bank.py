"""World Bank Indicators API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.worldbank.org/v2"


class WorldBankSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search development indicators via World Bank API",
            "auth_required": False,
            "data_type": "indicators",
            "rate_limit": "No formal limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/indicator",
                params={
                    "format": "json",
                    "per_page": max_results,
                    "search": query,
                },
            )
            resp.raise_for_status()
        except Exception:
            return []
        data = resp.json()
        if not isinstance(data, list) or len(data) < 2:
            return []
        indicators = data[1] or []
        return [self._indicator_to_doc(ind) for ind in indicators]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/country/all/indicator/{identifier}",
            params={"format": "json", "per_page": 100, "date": "2010:2024", "source": 2},
        )
        if resp.status_code == 404:
            return None
        try:
            resp.raise_for_status()
        except Exception:
            return None
        data = resp.json()
        if not isinstance(data, list) or len(data) < 2:
            return None
        records = data[1] or []
        if not records:
            return None
        # Build a summary from the data values
        values = [
            {
                "country": r.get("country", {}).get("value", ""),
                "year": r.get("date", ""),
                "value": r.get("value"),
            }
            for r in records
            if r.get("value") is not None
        ]
        return Document(
            source_id=f"wb:{identifier}",
            source_type="world_bank",
            title=records[0].get("indicator", {}).get("value", identifier),
            authors=[],
            year=None,
            doi=None,
            abstract=None,
            full_text=json.dumps(values, indent=2),
            url=f"https://data.worldbank.org/indicator/{identifier}",
            metadata={"indicator_id": identifier, "record_count": len(values)},
        )

    def _indicator_to_doc(self, ind: dict) -> Document:
        ind_id = ind.get("id", "")
        source_name = ind.get("source", {}).get("value", "") if isinstance(ind.get("source"), dict) else ""
        return Document(
            source_id=f"wb:{ind_id}",
            source_type="world_bank",
            title=ind.get("name", ""),
            authors=[],
            year=None,
            doi=None,
            abstract=ind.get("sourceNote", ""),
            url=f"https://data.worldbank.org/indicator/{ind_id}",
            metadata={"indicator_id": ind_id, "source": source_name},
        )
