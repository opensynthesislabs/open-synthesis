"""bioRxiv and medRxiv preprint API integration."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://api.biorxiv.org"
_WINDOW_DAYS = 90


class BiorxivSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search preprints from bioRxiv and medRxiv",
            "auth_required": False,
            "data_type": "preprints",
            "rate_limit": "No formal limit; be polite",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        end = datetime.now()
        start = end - timedelta(days=_WINDOW_DAYS)
        interval = f"{start:%Y-%m-%d}/{end:%Y-%m-%d}"
        terms = query.lower().split()

        docs: list[Document] = []
        for server in ("biorxiv", "medrxiv"):
            papers = await self._fetch_details(server, interval, cursor=0)
            for p in papers:
                text = f"{p.get('title', '')} {p.get('abstract', '')}".lower()
                if any(t in text for t in terms):
                    docs.append(self._to_doc(p))
                    if len(docs) >= max_results:
                        return docs
        return docs

    async def fetch(self, identifier: str) -> Document | None:
        # identifier is a DOI like 10.1101/2024.01.01.123456
        http = await self.client()
        resp = await http.get(f"{_BASE}/details/biorxiv/{identifier}/na/json")
        if resp.status_code == 404:
            return None
        try:
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            return None
        papers = data.get("collection", [])
        if not papers:
            return None
        return self._to_doc(papers[0])

    async def _fetch_details(
        self, server: str, interval: str, cursor: int
    ) -> list[dict]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/details/{server}/{interval}/{cursor}/json"
            )
            resp.raise_for_status()
            return resp.json().get("collection", [])
        except Exception:
            return []

    def _to_doc(self, paper: dict) -> Document:
        doi = paper.get("doi", "")
        authors = [a.strip() for a in paper.get("authors", "").split(";") if a.strip()]
        year = None
        date_str = paper.get("date", "")
        if date_str:
            try:
                year = int(date_str[:4])
            except (ValueError, IndexError):
                pass
        return Document(
            source_id=f"biorxiv:{doi}",
            source_type="biorxiv",
            title=paper.get("title", ""),
            authors=authors,
            year=year,
            doi=doi,
            abstract=paper.get("abstract"),
            url=f"https://doi.org/{doi}" if doi else None,
            metadata={"category": paper.get("category", "")},
        )
