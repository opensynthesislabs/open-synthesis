"""OpenAIRE Graph API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.openaire.eu/search"


class OpenAireSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "OpenAIRE open-access publications and research outputs",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "No formal limit for basic search",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/publications",
                params={"keywords": query, "format": "json", "size": max_results},
            )
            resp.raise_for_status()
        except Exception:
            return []
        data = resp.json()
        results = (
            data.get("response", {}).get("results", {}).get("result", [])
        )
        if not isinstance(results, list):
            return []
        return [self._to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/publications",
                params={"doi": identifier, "format": "json"},
            )
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
        except Exception:
            return None
        data = resp.json()
        results = (
            data.get("response", {}).get("results", {}).get("result", [])
        )
        if not results:
            return None
        return self._to_doc(results[0])

    def _to_doc(self, result: dict) -> Document:
        entity = result.get("metadata", {}).get("oaf:entity", {})
        oaf = entity.get("oaf:result", {})

        title_raw = oaf.get("title", {})
        if isinstance(title_raw, dict):
            title = title_raw.get("$", "")
        elif isinstance(title_raw, list) and title_raw:
            title = title_raw[0].get("$", "") if isinstance(title_raw[0], dict) else str(title_raw[0])
        else:
            title = str(title_raw) if title_raw else ""

        creators = oaf.get("creator", [])
        if isinstance(creators, dict):
            creators = [creators]
        authors = [c.get("$", "") for c in creators if isinstance(c, dict)]

        date = oaf.get("dateofacceptance", {})
        date_str = date.get("$", "") if isinstance(date, dict) else str(date) if date else ""
        year = int(date_str[:4]) if date_str and len(date_str) >= 4 else None

        # Extract DOI from persistent identifiers
        pids = oaf.get("pid", [])
        if isinstance(pids, dict):
            pids = [pids]
        doi = None
        oaire_id = ""
        for pid in pids:
            if not isinstance(pid, dict):
                continue
            if pid.get("@classid") == "doi":
                doi = pid.get("$", "")
            if not oaire_id:
                oaire_id = pid.get("$", "")

        desc = oaf.get("description", {})
        abstract = desc.get("$", "") if isinstance(desc, dict) else str(desc) if desc else ""

        header = result.get("header", {})
        obj_id = header.get("dri:objIdentifier", {})
        record_id = obj_id.get("$", "") if isinstance(obj_id, dict) else str(obj_id) if obj_id else ""

        return Document(
            source_id=f"openaire:{record_id or doi or oaire_id}",
            source_type="openaire",
            title=title,
            authors=authors[:10],
            year=year,
            doi=doi,
            abstract=abstract,
            url=f"https://explore.openaire.eu/search/publication?pid={doi}" if doi else None,
        )
