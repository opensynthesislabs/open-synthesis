"""arXiv API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://export.arxiv.org/api/query"


class ArxivSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search preprints on arXiv",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "3 sec delay between requests",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        import xml.etree.ElementTree as ET

        http = await self.client()
        resp = await http.get(
            _BASE,
            params={"search_query": f"all:{query}", "max_results": max_results},
        )
        resp.raise_for_status()

        ns = {"atom": "http://www.w3.org/2005/Atom"}
        root = ET.fromstring(resp.text)
        docs = []
        for entry in root.findall("atom:entry", ns):
            arxiv_id = (entry.findtext("atom:id", "", ns) or "").split("/abs/")[-1]
            title = entry.findtext("atom:title", "", ns).strip().replace("\n", " ")
            summary = entry.findtext("atom:summary", "", ns).strip()
            authors = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)]
            published = entry.findtext("atom:published", "", ns)
            year = int(published[:4]) if published else None

            link = None
            for l in entry.findall("atom:link", ns):
                if l.get("type") == "application/pdf":
                    link = l.get("href")

            docs.append(Document(
                source_id=f"arxiv:{arxiv_id}",
                source_type="arxiv",
                title=title,
                authors=authors,
                year=year,
                abstract=summary,
                url=link or f"https://arxiv.org/abs/{arxiv_id}",
            ))
        return docs

    async def fetch(self, identifier: str) -> Document | None:
        results = await self.search(f"id:{identifier}", max_results=1)
        return results[0] if results else None
