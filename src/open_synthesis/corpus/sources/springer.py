"""Springer Nature API integration."""

from __future__ import annotations

import os
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.springernature.com/meta/v2/json"


class SpringerSource(DataSource):
    def __init__(self, api_key: str | None = None) -> None:
        super().__init__(api_key=api_key)
        self._springer_key = api_key or os.environ.get("SPRINGER_API_KEY", "")

    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Springer Nature metadata and open-access publications",
            "auth_required": True,
            "data_type": "publications",
            "rate_limit": "500 requests/day with free API key",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        if not self._springer_key:
            return []
        http = await self.client()
        resp = await http.get(
            _BASE,
            params={"q": query, "p": max_results, "api_key": self._springer_key},
        )
        resp.raise_for_status()
        records = resp.json().get("records", [])
        return [self._to_doc(r) for r in records]

    async def fetch(self, identifier: str) -> Document | None:
        if not self._springer_key:
            return None
        http = await self.client()
        resp = await http.get(
            _BASE,
            params={"q": f"doi:{identifier}", "p": 1, "api_key": self._springer_key},
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        records = resp.json().get("records", [])
        if not records:
            return None
        return self._to_doc(records[0])

    def _to_doc(self, record: dict) -> Document:
        authors = [
            c.get("creator", "") for c in record.get("creators", [])
            if c.get("creator")
        ]
        doi = record.get("doi", "")
        year = None
        pub_date = record.get("publicationDate", "")
        if pub_date and len(pub_date) >= 4:
            try:
                year = int(pub_date[:4])
            except ValueError:
                pass
        return Document(
            source_id=f"springer:{doi}" if doi else f"springer:{record.get('title', '')[:40]}",
            source_type="springer",
            title=record.get("title", ""),
            authors=authors,
            year=year,
            doi=doi,
            abstract=record.get("abstract", ""),
            url=record.get("url", [{}])[0].get("value", "") if isinstance(record.get("url"), list) else record.get("url", ""),
        )
