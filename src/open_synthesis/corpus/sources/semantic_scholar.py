"""Semantic Scholar API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.semanticscholar.org/graph/v1"
_FIELDS = "paperId,title,abstract,authors,year,externalIds,url"


class SemanticScholarSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search academic papers via Semantic Scholar API",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "100 requests/5 min (unauthenticated)",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        resp = await http.get(
            f"{_BASE}/paper/search",
            params={"query": query, "limit": max_results, "fields": _FIELDS},
            headers=headers,
        )
        resp.raise_for_status()
        papers = resp.json().get("data", [])
        return [self._to_doc(p) for p in papers]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        headers = {"x-api-key": self.api_key} if self.api_key else {}
        resp = await http.get(
            f"{_BASE}/paper/{identifier}",
            params={"fields": _FIELDS},
            headers=headers,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._to_doc(resp.json())

    def _to_doc(self, paper: dict) -> Document:
        authors = [a.get("name", "") for a in paper.get("authors", [])]
        ext = paper.get("externalIds", {}) or {}
        return Document(
            source_id=f"s2:{paper['paperId']}",
            source_type="semantic_scholar",
            title=paper.get("title", ""),
            authors=authors,
            year=paper.get("year"),
            doi=ext.get("DOI"),
            abstract=paper.get("abstract"),
            url=paper.get("url"),
        )
