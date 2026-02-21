"""OpenCitations API integration."""

from __future__ import annotations

import re
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://opencitations.net/index/api/v2"
_DOI_RE = re.compile(r"^10\.\d{4,9}/[^\s]+$")


class OpenCitationsSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Citation data and metadata from OpenCitations",
            "auth_required": False,
            "data_type": "citations",
            "rate_limit": "180 requests/min",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        query = query.strip()
        if not _DOI_RE.match(query):
            return []
        http = await self.client()
        resp = await http.get(f"{_BASE}/citations/doi:{query}")
        if resp.status_code != 200:
            return []
        citations = resp.json() if isinstance(resp.json(), list) else []
        docs: list[Document] = []
        seen: set[str] = set()
        for cit in citations[:max_results]:
            citing = cit.get("citing", "")
            cited = cit.get("cited", "")
            for doi in (citing, cited):
                if doi and doi != query and doi not in seen:
                    seen.add(doi)
                    docs.append(Document(
                        source_id=f"oc:{doi}",
                        source_type="opencitations",
                        title=f"Related to {query}",
                        doi=doi,
                        metadata={
                            "relation": "citing" if doi == citing else "cited",
                            "timespan": cit.get("timespan", ""),
                            "creation": cit.get("creation", ""),
                        },
                    ))
        # Enrich with metadata where possible
        for doc in docs[:max_results]:
            meta = await self._fetch_metadata(doc.doi or "")
            if meta:
                doc.title = meta.get("title", doc.title)
                doc.authors = [
                    a.strip()
                    for a in meta.get("author", "").split(";")
                    if a.strip()
                ]
                try:
                    doc.year = int(meta.get("year", ""))
                except (ValueError, TypeError):
                    pass
        return docs[:max_results]

    async def fetch(self, identifier: str) -> Document | None:
        meta = await self._fetch_metadata(identifier)
        if not meta:
            return None
        authors = [a.strip() for a in meta.get("author", "").split(";") if a.strip()]
        year = None
        try:
            year = int(meta.get("year", ""))
        except (ValueError, TypeError):
            pass
        return Document(
            source_id=f"oc:{identifier}",
            source_type="opencitations",
            title=meta.get("title", ""),
            authors=authors,
            year=year,
            doi=identifier,
            metadata={
                "source_title": meta.get("source_title", ""),
                "citation_count": meta.get("citation_count", ""),
            },
        )

    async def _fetch_metadata(self, doi: str) -> dict | None:
        if not doi:
            return None
        http = await self.client()
        resp = await http.get(f"{_BASE}/metadata/doi:{doi}")
        if resp.status_code != 200:
            return None
        data = resp.json()
        if isinstance(data, list) and data:
            return data[0]
        return None
