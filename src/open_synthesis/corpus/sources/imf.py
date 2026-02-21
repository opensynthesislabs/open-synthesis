"""IMF Data API (SDMX-JSON) integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "http://dataservices.imf.org/REST/SDMX_JSON.svc"


class ImfSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "IMF macroeconomic and financial data via SDMX-JSON",
            "auth_required": False,
            "data_type": "statistics",
            "rate_limit": "No published limit; be respectful",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        resp = await http.get(f"{_BASE}/Dataflow")
        resp.raise_for_status()
        dataflows = (
            resp.json()
            .get("Structure", {})
            .get("Dataflows", {})
            .get("Dataflow", [])
        )
        q = query.lower()
        matches = [
            df for df in dataflows
            if q in (df.get("Name", {}).get("#text", "") or "").lower()
            or q in (df.get("@id", "") or "").lower()
        ]
        return [self._dataflow_to_doc(df) for df in matches[:max_results]]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        url = f"{_BASE}/CompactData/{identifier}/A..?startPeriod=2010&endPeriod=2024"
        resp = await http.get(url)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        data = resp.json()
        series_list = (
            data.get("CompactData", {})
            .get("DataSet", {})
            .get("Series", [])
        )
        if isinstance(series_list, dict):
            series_list = [series_list]
        observations = []
        for series in series_list[:50]:
            obs = series.get("Obs", [])
            if isinstance(obs, dict):
                obs = [obs]
            for o in obs:
                observations.append({
                    "period": o.get("@TIME_PERIOD", ""),
                    "value": o.get("@OBS_VALUE", ""),
                })
        return Document(
            source_id=f"imf:{identifier}",
            source_type="imf",
            title=f"IMF Dataflow: {identifier}",
            full_text=json.dumps(observations, indent=2) if observations else None,
            metadata={"dataflow_id": identifier, "series_count": len(series_list)},
        )

    def _dataflow_to_doc(self, df: dict) -> Document:
        dataflow_id = df.get("@id", "")
        name = df.get("Name", {}).get("#text", "") or dataflow_id
        return Document(
            source_id=f"imf:{dataflow_id}",
            source_type="imf",
            title=name,
            abstract=f"IMF dataflow: {name} ({dataflow_id})",
            metadata={"dataflow_id": dataflow_id},
        )
