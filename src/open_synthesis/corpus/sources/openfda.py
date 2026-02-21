"""OpenFDA drug labels and adverse events API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.fda.gov"


class OpenFdaSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "FDA drug labels and adverse event reports via openFDA API",
            "auth_required": False,
            "data_type": "regulatory",
            "rate_limit": "240 requests/min without key, 120k/day with key",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        params: dict[str, Any] = {
            "search": query,
            "limit": min(max_results, 99),
        }
        if self.api_key:
            params["api_key"] = self.api_key
        try:
            resp = await http.get(f"{_BASE}/drug/label.json", params=params)
            if resp.status_code != 200:
                return []
            results = resp.json().get("results", [])
        except Exception:
            return []
        return [self._label_to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        """Fetch adverse events for a drug by generic name or set_id."""
        http = await self.client()
        params: dict[str, Any] = {
            "search": f'openfda.spl_set_id:"{identifier}"',
            "limit": 1,
        }
        if self.api_key:
            params["api_key"] = self.api_key
        try:
            resp = await http.get(f"{_BASE}/drug/label.json", params=params)
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                return None
            results = resp.json().get("results", [])
        except Exception:
            return None
        if not results:
            return None
        doc = self._label_to_doc(results[0])

        # Enrich with adverse event data
        generic = results[0].get("openfda", {}).get("generic_name", [""])[0]
        if generic:
            ae_params: dict[str, Any] = {
                "search": f'patient.drug.openfda.generic_name:"{generic}"',
                "limit": 10,
            }
            if self.api_key:
                ae_params["api_key"] = self.api_key
            try:
                ae_resp = await http.get(f"{_BASE}/drug/event.json", params=ae_params)
                if ae_resp.status_code == 200:
                    events = ae_resp.json().get("results", [])
                    doc.full_text = json.dumps(
                        [
                            {
                                "report_id": e.get("safetyreportid", ""),
                                "reactions": [
                                    r.get("reactionmeddrapt", "")
                                    for r in e.get("patient", {}).get("reaction", [])
                                ],
                                "date": e.get("receivedate", ""),
                            }
                            for e in events
                        ],
                        indent=2,
                    )
            except Exception:
                pass

        return doc

    def _label_to_doc(self, label: dict) -> Document:
        openfda = label.get("openfda", {})
        brand = openfda.get("brand_name", [""])[0]
        generic = openfda.get("generic_name", [""])[0]
        set_id = label.get("set_id", openfda.get("spl_set_id", [""])[0])
        title = brand or generic or "Unknown drug"

        desc_parts = []
        for field in ("description", "indications_and_usage", "warnings"):
            val = label.get(field, [])
            if val:
                desc_parts.append(val[0] if isinstance(val, list) else val)

        return Document(
            source_id=f"fda:{set_id}",
            source_type="openfda",
            title=title,
            abstract="\n\n".join(desc_parts) if desc_parts else None,
            url=f"https://api.fda.gov/drug/label.json?search=set_id:{set_id}",
            metadata={
                "brand_name": brand,
                "generic_name": generic,
                "set_id": set_id,
                "manufacturer": openfda.get("manufacturer_name", [""])[0],
                "route": openfda.get("route", []),
            },
        )
