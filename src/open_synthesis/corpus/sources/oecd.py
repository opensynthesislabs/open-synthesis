"""OECD SDMX API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://sdmx.oecd.org/public/rest"


class OecdSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "OECD statistical data via SDMX REST API",
            "auth_required": False,
            "data_type": "statistics",
            "rate_limit": "No official limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        """Search OECD dataflows (datasets) matching the query."""
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/dataflow/OECD",
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        data = resp.json()

        dataflows = data.get("data", {}).get("dataflows", [])
        query_lower = query.lower()
        matched = []
        for df in dataflows:
            name = df.get("name", "")
            desc = df.get("description", "")
            if isinstance(name, dict):
                name = name.get("en", str(name))
            if isinstance(desc, dict):
                desc = desc.get("en", str(desc))
            if query_lower in name.lower() or query_lower in desc.lower():
                matched.append(Document(
                    source_id=f"oecd:{df.get('id', '')}",
                    source_type="oecd",
                    title=name,
                    abstract=desc,
                    metadata={"dataflow_id": df.get("id", "")},
                ))
            if len(matched) >= max_results:
                break
        return matched

    async def fetch(self, identifier: str) -> Document | None:
        """Fetch data from an OECD dataflow by ID."""
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/data/OECD,{identifier}/all",
            headers={"Accept": "application/json"},
            params={"lastNObservations": "10"},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        return Document(
            source_id=f"oecd:{identifier}",
            source_type="oecd",
            title=f"OECD dataset: {identifier}",
            full_text=json.dumps(data, indent=2)[:10000],
            metadata={"dataflow_id": identifier},
        )
