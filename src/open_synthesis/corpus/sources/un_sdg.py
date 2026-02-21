"""UN Sustainable Development Goals API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://unstats.un.org/sdgapi/v1"


class UnSdgSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "UN SDG indicators and observation data",
            "auth_required": False,
            "data_type": "statistics",
            "rate_limit": "No formal limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(f"{_BASE}/sdg/Indicator/List")
            resp.raise_for_status()
        except Exception:
            return []
        indicators = resp.json()
        if not isinstance(indicators, list):
            return []
        query_lower = query.lower()
        matched = [
            ind for ind in indicators
            if query_lower in (ind.get("description", "") or "").lower()
            or query_lower in (ind.get("code", "") or "").lower()
        ]
        return [self._to_doc(ind) for ind in matched[:max_results]]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/sdg/Indicator/Data",
                params={"indicator": identifier, "pageSize": 100},
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
        except Exception:
            return None
        data = resp.json()
        observations = data.get("data", [])
        # Build a text summary from observations
        lines = [f"Indicator {identifier} observations:"]
        for obs in observations[:50]:
            geo = obs.get("geoAreaName", "")
            year = obs.get("timePeriodStart", "")
            value = obs.get("value", "")
            lines.append(f"  {geo} ({year}): {value}")
        return Document(
            source_id=f"unsdg:{identifier}",
            source_type="un_sdg",
            title=f"SDG Indicator {identifier}",
            full_text="\n".join(lines) if observations else None,
            url=f"https://unstats.un.org/sdgs/indicators/database/?indicator={identifier}",
            metadata={
                "indicator_code": identifier,
                "observation_count": len(observations),
            },
        )

    def _to_doc(self, indicator: dict) -> Document:
        code = indicator.get("code", "")
        target = indicator.get("target", "")
        return Document(
            source_id=f"unsdg:{code}",
            source_type="un_sdg",
            title=indicator.get("description", code),
            abstract=f"Target: {target}" if target else None,
            url=f"https://unstats.un.org/sdgs/indicators/database/?indicator={code}",
            metadata={
                "indicator_code": code,
                "target": target,
                "goal": indicator.get("goal", ""),
            },
        )
