"""Unpaywall API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.unpaywall.org/v2"
_EMAIL = "support@opensynthesis.dev"


class UnpaywallSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Find open-access versions of papers via Unpaywall",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "100k requests/day with email",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/search",
                params={"query": query, "email": _EMAIL},
            )
            resp.raise_for_status()
        except Exception:
            return []
        results = resp.json().get("results", [])
        docs = []
        for item in results[:max_results]:
            r = item.get("response", {})
            if r:
                docs.append(self._to_doc(r))
        return docs

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/{identifier}",
            params={"email": _EMAIL},
        )
        if resp.status_code == 404:
            return None
        try:
            resp.raise_for_status()
        except Exception:
            return None
        return self._to_doc(resp.json())

    def _to_doc(self, item: dict) -> Document:
        doi = item.get("doi", "")
        authors = []
        for a in item.get("z_authors", []) or []:
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)
        year = item.get("year")
        oa_loc = item.get("best_oa_location") or {}
        pdf_url = oa_loc.get("url_for_pdf")
        oa_url = oa_loc.get("url") or oa_loc.get("url_for_landing_page")
        return Document(
            source_id=f"unpaywall:{doi}",
            source_type="unpaywall",
            title=item.get("title", ""),
            authors=authors,
            year=year,
            doi=doi,
            abstract=None,
            url=oa_url or (f"https://doi.org/{doi}" if doi else None),
            metadata={"pdf_url": pdf_url, "is_oa": item.get("is_oa", False)},
        )
