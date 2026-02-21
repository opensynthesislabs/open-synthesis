"""WHO Global Health Observatory API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://ghoapi.azureedge.net/api"


class WhoGhoSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search global health indicators via WHO GHO OData API",
            "auth_required": False,
            "data_type": "indicators",
            "rate_limit": "No formal limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        # OData filter: contains(IndicatorName,'query')
        safe_query = query.replace("'", "''")
        try:
            resp = await http.get(
                f"{_BASE}/Indicator",
                params={"$filter": f"contains(IndicatorName,'{safe_query}')"},
            )
            resp.raise_for_status()
        except Exception:
            return []
        indicators = resp.json().get("value", [])
        docs = []
        for ind in indicators[:max_results]:
            docs.append(self._indicator_to_doc(ind))
        return docs

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/{identifier}",
            params={"$top": 100, "$orderby": "TimeDim desc"},
        )
        if resp.status_code == 404:
            return None
        try:
            resp.raise_for_status()
        except Exception:
            return None
        data = resp.json().get("value", [])
        if not data:
            return None
        observations = [
            {
                "country": r.get("SpatialDim", ""),
                "year": r.get("TimeDim", ""),
                "value": r.get("NumericValue"),
                "dim": r.get("Dim1", ""),
            }
            for r in data
        ]
        return Document(
            source_id=f"who:{identifier}",
            source_type="who_gho",
            title=identifier,
            authors=[],
            year=None,
            doi=None,
            abstract=None,
            full_text=json.dumps(observations, indent=2),
            url=f"https://www.who.int/data/gho/data/indicators/indicator-details/GHO/{identifier}",
            metadata={"indicator_code": identifier, "record_count": len(observations)},
        )

    def _indicator_to_doc(self, ind: dict) -> Document:
        code = ind.get("IndicatorCode", "")
        name = ind.get("IndicatorName", "")
        return Document(
            source_id=f"who:{code}",
            source_type="who_gho",
            title=name,
            authors=[],
            year=None,
            doi=None,
            abstract=None,
            url=f"https://www.who.int/data/gho/data/indicators/indicator-details/GHO/{code}",
            metadata={"indicator_code": code},
        )
