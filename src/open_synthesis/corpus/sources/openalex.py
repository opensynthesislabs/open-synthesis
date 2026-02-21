"""OpenAlex API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.openalex.org"


class OpenAlexSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Large-scale academic paper search via OpenAlex",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "10 requests/sec (polite pool with mailto)",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        params: dict[str, Any] = {
            "search": query,
            "per_page": max_results,
        }
        if self.api_key:
            params["api_key"] = self.api_key
        resp = await http.get(
            f"{_BASE}/works",
            params=params,
            headers={"User-Agent": "OpenSynthesis/0.1 (mailto:support@opensynthesis.dev)"},
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return [self._to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(f"{_BASE}/works/{identifier}")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return self._to_doc(resp.json())

    def _to_doc(self, item: dict) -> Document:
        authors = []
        for authorship in item.get("authorships", []):
            name = authorship.get("author", {}).get("display_name", "")
            if name:
                authors.append(name)
        abstract = None
        inv_index = item.get("abstract_inverted_index")
        if inv_index:
            # Reconstruct abstract from inverted index
            words: dict[int, str] = {}
            for word, positions in inv_index.items():
                for pos in positions:
                    words[pos] = word
            abstract = " ".join(words[i] for i in sorted(words))
        return Document(
            source_id=f"openalex:{item.get('id', '').split('/')[-1]}",
            source_type="openalex",
            title=item.get("title", ""),
            authors=authors,
            year=item.get("publication_year"),
            doi=item.get("doi", "").replace("https://doi.org/", "") if item.get("doi") else None,
            abstract=abstract,
            url=item.get("doi") or item.get("id"),
        )
