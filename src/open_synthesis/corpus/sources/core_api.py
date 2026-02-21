"""CORE API integration (full-text open access papers)."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.core.ac.uk/v3"


class CoreSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Full-text open access papers via CORE API",
            "auth_required": True,
            "data_type": "papers",
            "rate_limit": "10 requests/sec with free API key",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        if not self.api_key:
            return []
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/search/works",
            params={"q": query, "limit": max_results},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [self._to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        if not self.api_key:
            return None
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/works/{identifier}",
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._to_doc(resp.json())

    def _to_doc(self, item: dict) -> Document:
        authors = [a.get("name", "") for a in item.get("authors", []) if a.get("name")]
        return Document(
            source_id=f"core:{item.get('id', '')}",
            source_type="core",
            title=item.get("title", ""),
            authors=authors,
            year=item.get("yearPublished"),
            doi=item.get("doi"),
            abstract=item.get("abstract"),
            full_text=item.get("fullText"),
            url=item.get("downloadUrl") or item.get("sourceFulltextUrls", [None])[0] if item.get("sourceFulltextUrls") else None,
        )
