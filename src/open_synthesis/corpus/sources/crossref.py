"""CrossRef API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.crossref.org/works"


class CrossrefSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "DOI resolution and bibliographic metadata via CrossRef",
            "auth_required": False,
            "data_type": "metadata",
            "rate_limit": "50 requests/sec with polite pool (mailto header)",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        resp = await http.get(
            _BASE,
            params={"query": query, "rows": max_results},
            headers={"User-Agent": "OpenSynthesis/0.1 (mailto:support@opensynthesis.dev)"},
        )
        resp.raise_for_status()
        items = resp.json().get("message", {}).get("items", [])
        return [self._to_doc(item) for item in items]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/{identifier}",
            headers={"User-Agent": "OpenSynthesis/0.1 (mailto:support@opensynthesis.dev)"},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._to_doc(resp.json().get("message", {}))

    def _to_doc(self, item: dict) -> Document:
        title_list = item.get("title", [])
        title = title_list[0] if title_list else ""
        authors = []
        for a in item.get("author", []):
            name = f"{a.get('given', '')} {a.get('family', '')}".strip()
            if name:
                authors.append(name)
        year = None
        date_parts = item.get("published-print", item.get("published-online", {}))
        if date_parts and date_parts.get("date-parts"):
            year = date_parts["date-parts"][0][0]
        abstract = item.get("abstract", "")
        doi = item.get("DOI", "")
        return Document(
            source_id=f"doi:{doi}" if doi else f"crossref:{title[:40]}",
            source_type="crossref",
            title=title,
            authors=authors,
            year=year,
            doi=doi,
            abstract=abstract,
            url=item.get("URL", ""),
        )
