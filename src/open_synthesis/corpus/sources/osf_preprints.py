"""OSF Preprints API integration (PsyArXiv, SocArXiv, EarthArXiv, etc.)."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.osf.io/v2"


class OsfPreprintsSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Preprints from OSF (PsyArXiv, SocArXiv, EarthArXiv, etc.)",
            "auth_required": False,
            "data_type": "preprints",
            "rate_limit": "100 requests/hour unauthenticated",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/preprints/",
                params={
                    "filter[title,description]": query,
                    "page[size]": min(max_results, 100),
                },
            )
            if resp.status_code != 200:
                return []
            data = resp.json().get("data", [])
        except Exception:
            return []
        return [self._to_doc(item) for item in data]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(f"{_BASE}/preprints/{identifier}/")
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                return None
            item = resp.json().get("data")
        except Exception:
            return None
        if not item:
            return None
        return self._to_doc(item)

    def _to_doc(self, item: dict) -> Document:
        attrs = item.get("attributes", {})
        preprint_id = item.get("id", "")
        title = attrs.get("title", "")
        description = attrs.get("description", "")
        doi = attrs.get("doi", "") or attrs.get("preprint_doi_created", "")
        date_published = attrs.get("date_published", "")

        year = None
        if date_published:
            try:
                year = int(date_published[:4])
            except (ValueError, IndexError):
                pass

        # Extract provider info
        provider = ""
        relationships = item.get("relationships", {})
        provider_data = relationships.get("provider", {}).get("data", {})
        if isinstance(provider_data, dict):
            provider = provider_data.get("id", "")

        return Document(
            source_id=f"osf:{preprint_id}",
            source_type="osf_preprints",
            title=title,
            year=year,
            doi=doi if doi else None,
            abstract=description if description else None,
            url=f"https://osf.io/preprints/{preprint_id}",
            metadata={
                "provider": provider,
                "date_published": date_published,
            },
        )
