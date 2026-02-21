"""FRED (Federal Reserve Economic Data) API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.stlouisfed.org/fred"


class FredSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Federal Reserve economic time series data",
            "auth_required": True,
            "data_type": "statistics",
            "rate_limit": "120 requests/min with free API key",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        if not self.api_key:
            return []
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/series/search",
            params={
                "search_text": query,
                "limit": max_results,
                "api_key": self.api_key,
                "file_type": "json",
            },
        )
        resp.raise_for_status()
        serieses = resp.json().get("seriess", [])
        return [self._series_to_doc(s) for s in serieses]

    async def fetch(self, identifier: str) -> Document | None:
        """Fetch a FRED series by ID, including observations."""
        if not self.api_key:
            return None
        http = await self.client()
        # Get series info
        resp = await http.get(
            f"{_BASE}/series",
            params={"series_id": identifier, "api_key": self.api_key, "file_type": "json"},
        )
        if resp.status_code == 400:
            return None
        resp.raise_for_status()
        serieses = resp.json().get("seriess", [])
        if not serieses:
            return None
        doc = self._series_to_doc(serieses[0])

        # Get observations
        obs_resp = await http.get(
            f"{_BASE}/series/observations",
            params={"series_id": identifier, "api_key": self.api_key, "file_type": "json"},
        )
        obs_resp.raise_for_status()
        observations = obs_resp.json().get("observations", [])
        doc.full_text = json.dumps(
            [{"date": o["date"], "value": o["value"]} for o in observations[-100:]],
            indent=2,
        )
        return doc

    def _series_to_doc(self, series: dict) -> Document:
        return Document(
            source_id=f"fred:{series.get('id', '')}",
            source_type="fred",
            title=series.get("title", ""),
            abstract=series.get("notes", ""),
            metadata={
                "frequency": series.get("frequency", ""),
                "units": series.get("units", ""),
                "seasonal_adjustment": series.get("seasonal_adjustment", ""),
            },
        )
