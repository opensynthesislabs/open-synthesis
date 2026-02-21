"""PubMed E-utilities integration."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"


class PubMedSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Search biomedical literature via PubMed E-utilities",
            "auth_required": False,
            "data_type": "papers",
            "rate_limit": "3 requests/sec (unauthenticated), 10/sec with API key",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        params: dict[str, Any] = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        resp = await http.get(_ESEARCH, params=params)
        resp.raise_for_status()
        ids = resp.json().get("esearchresult", {}).get("idlist", [])
        if not ids:
            return []
        return await self._fetch_batch(ids)

    async def fetch(self, identifier: str) -> Document | None:
        docs = await self._fetch_batch([identifier])
        return docs[0] if docs else None

    async def _fetch_batch(self, pmids: list[str]) -> list[Document]:
        http = await self.client()
        params: dict[str, Any] = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        if self.api_key:
            params["api_key"] = self.api_key

        resp = await http.get(_EFETCH, params=params)
        resp.raise_for_status()

        root = ET.fromstring(resp.text)
        docs = []
        for article in root.findall(".//PubmedArticle"):
            medline = article.find(".//MedlineCitation")
            if medline is None:
                continue
            pmid = medline.findtext("PMID", "")
            art = medline.find(".//Article")
            if art is None:
                continue

            title = art.findtext("ArticleTitle", "")
            abstract_el = art.find(".//Abstract/AbstractText")
            abstract = abstract_el.text if abstract_el is not None and abstract_el.text else None
            authors = []
            for author in art.findall(".//AuthorList/Author"):
                last = author.findtext("LastName", "")
                fore = author.findtext("ForeName", "")
                if last:
                    authors.append(f"{fore} {last}".strip())

            year = None
            pub_date = art.find(".//Journal/JournalIssue/PubDate/Year")
            if pub_date is not None and pub_date.text:
                year = int(pub_date.text)

            doi = None
            for eid in article.findall(".//PubmedData/ArticleIdList/ArticleId"):
                if eid.get("IdType") == "doi":
                    doi = eid.text

            docs.append(Document(
                source_id=f"pmid:{pmid}",
                source_type="pubmed",
                title=title,
                authors=authors,
                year=year,
                doi=doi,
                abstract=abstract,
                url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            ))
        return docs
