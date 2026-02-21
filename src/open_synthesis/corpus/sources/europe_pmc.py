"""Europe PMC API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://www.ebi.ac.uk/europepmc/webservices/rest"


class EuropePmcSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search biomedical literature via Europe PMC",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "No formal limit; be polite",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/search",
                params={
                    "query": query,
                    "format": "json",
                    "pageSize": max_results,
                    "resultType": "core",
                },
            )
            resp.raise_for_status()
        except Exception:
            return []
        results = resp.json().get("resultList", {}).get("result", [])
        return [self._to_doc(r) for r in results]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/search",
            params={
                "query": f"DOI:{identifier}",
                "format": "json",
                "resultType": "core",
            },
        )
        if resp.status_code == 404:
            return None
        try:
            resp.raise_for_status()
        except Exception:
            return None
        results = resp.json().get("resultList", {}).get("result", [])
        if not results:
            return None
        return self._to_doc(results[0])

    def _to_doc(self, item: dict) -> Document:
        pmid = item.get("id", "")
        authors_str = item.get("authorString", "")
        authors = [a.strip() for a in authors_str.split(",") if a.strip()]
        year = None
        pub_year = item.get("pubYear")
        if pub_year:
            try:
                year = int(pub_year)
            except (ValueError, TypeError):
                pass
        doi = item.get("doi")
        return Document(
            source_id=f"europepmc:{pmid}",
            source_type="europe_pmc",
            title=item.get("title", ""),
            authors=authors,
            year=year,
            doi=doi,
            abstract=item.get("abstractText"),
            url=f"https://europepmc.org/article/MED/{pmid}" if pmid else None,
            metadata={"source": item.get("source", "")},
        )
