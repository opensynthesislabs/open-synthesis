"""ClinicalTrials.gov v2 API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://clinicaltrials.gov/api/v2"


class ClinicalTrialsSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Clinical trial metadata from ClinicalTrials.gov v2 API",
            "auth_required": False,
            "data_type": "trials",
            "rate_limit": "No official limit; be respectful",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/studies",
            params={
                "query.term": query,
                "pageSize": max_results,
                "format": "json",
            },
        )
        resp.raise_for_status()
        studies = resp.json().get("studies", [])
        return [self._to_doc(s) for s in studies]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(f"{_BASE}/studies/{identifier}", params={"format": "json"})
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._to_doc(resp.json())

    def _to_doc(self, study: dict) -> Document:
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        desc = proto.get("descriptionModule", {})
        status = proto.get("statusModule", {})
        contacts = proto.get("contactsLocationsModule", {})

        nct_id = ident.get("nctId", "")
        title = ident.get("officialTitle") or ident.get("briefTitle", "")
        brief_summary = desc.get("briefSummary", "")
        detailed = desc.get("detailedDescription", "")

        investigators = []
        for inv in contacts.get("overallOfficials", []):
            name = inv.get("name", "")
            if name:
                investigators.append(name)

        return Document(
            source_id=f"nct:{nct_id}",
            source_type="clinicaltrials",
            title=title,
            authors=investigators,
            abstract=brief_summary,
            full_text=detailed if detailed else None,
            url=f"https://clinicaltrials.gov/study/{nct_id}",
            metadata={
                "status": status.get("overallStatus", ""),
                "phase": proto.get("designModule", {}).get("phases", []),
            },
        )
