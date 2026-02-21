"""Eurostat statistical data API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_SDMX_BASE = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1"
_STAT_BASE = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0"


class EurostatSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "European statistical datasets from Eurostat",
            "auth_required": False,
            "data_type": "statistics",
            "rate_limit": "No official limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_SDMX_BASE}/dataflow/ESTAT/all",
                params={"detail": "allstubs", "references": "none"},
                headers={
                    "Accept": "application/vnd.sdmx.structure+json;version=2.0.0",
                },
            )
            if resp.status_code != 200:
                return []
            data = resp.json()
        except Exception:
            return []

        dataflows = (
            data.get("data", {}).get("dataflows", [])
            or data.get("Structure", {}).get("Dataflows", {}).get("Dataflow", [])
        )

        query_lower = query.lower()
        matches = []
        for df in dataflows:
            name = self._get_name(df)
            desc = self._get_description(df)
            if query_lower in name.lower() or query_lower in desc.lower():
                matches.append(df)
                if len(matches) >= max_results:
                    break

        return [self._dataflow_to_doc(df) for df in matches]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_STAT_BASE}/data/{identifier}",
                params={"format": "JSON", "lang": "en"},
            )
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                return None
            data = resp.json()
        except Exception:
            return None

        label = data.get("label", identifier)
        dimensions = data.get("dimension", {})
        dim_summary = {}
        for dim_name, dim_info in dimensions.items():
            categories = dim_info.get("category", {}).get("label", {})
            dim_summary[dim_name] = list(categories.values())[:20]

        return Document(
            source_id=f"eurostat:{identifier}",
            source_type="eurostat",
            title=label,
            abstract=f"Eurostat dataset {identifier} with dimensions: {', '.join(dimensions.keys())}",
            full_text=json.dumps(dim_summary, indent=2),
            url=f"https://ec.europa.eu/eurostat/databrowser/view/{identifier}/default/table",
            metadata={
                "dataset_code": identifier,
                "dimensions": list(dimensions.keys()),
            },
        )

    def _get_name(self, df: dict) -> str:
        name = df.get("name", "")
        if isinstance(name, dict):
            return name.get("en", "") or next(iter(name.values()), "")
        if isinstance(name, list):
            for n in name:
                if isinstance(n, dict) and n.get("lang") == "en":
                    return n.get("value", "")
            return name[0].get("value", "") if name else ""
        return str(name)

    def _get_description(self, df: dict) -> str:
        desc = df.get("description", "")
        if isinstance(desc, dict):
            return desc.get("en", "") or next(iter(desc.values()), "")
        if isinstance(desc, list):
            for d in desc:
                if isinstance(d, dict) and d.get("lang") == "en":
                    return d.get("value", "")
            return desc[0].get("value", "") if desc else ""
        return str(desc) if desc else ""

    def _dataflow_to_doc(self, df: dict) -> Document:
        code = df.get("id", "")
        name = self._get_name(df)
        desc = self._get_description(df)

        return Document(
            source_id=f"eurostat:{code}",
            source_type="eurostat",
            title=name or code,
            abstract=desc if desc else None,
            url=f"https://ec.europa.eu/eurostat/databrowser/view/{code}/default/table",
            metadata={"dataset_code": code},
        )
