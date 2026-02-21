"""NCBI E-utilities Gene database integration."""

from __future__ import annotations

import os
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


class NcbiGeneSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "NCBI Gene database via E-utilities (gene records, summaries)",
            "auth_required": False,
            "data_type": "genomics",
            "rate_limit": "3 requests/sec (10/sec with API key)",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        api_key = self.api_key or os.environ.get("NCBI_API_KEY", "")
        params: dict[str, Any] = {
            "db": "gene",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
        }
        if api_key:
            params["api_key"] = api_key
        try:
            resp = await http.get(f"{_BASE}/esearch.fcgi", params=params)
            resp.raise_for_status()
        except Exception:
            return []
        id_list = resp.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            return []

        # Fetch summaries for all returned IDs
        sum_params: dict[str, Any] = {
            "db": "gene",
            "id": ",".join(id_list),
            "retmode": "json",
        }
        if api_key:
            sum_params["api_key"] = api_key
        try:
            sum_resp = await http.get(f"{_BASE}/esummary.fcgi", params=sum_params)
            sum_resp.raise_for_status()
        except Exception:
            return []
        result = sum_resp.json().get("result", {})
        docs: list[Document] = []
        for gid in id_list:
            gene = result.get(gid)
            if not gene:
                continue
            docs.append(self._to_doc(gid, gene))
        return docs

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        api_key = self.api_key or os.environ.get("NCBI_API_KEY", "")
        params: dict[str, Any] = {
            "db": "gene",
            "id": identifier,
            "retmode": "json",
        }
        if api_key:
            params["api_key"] = api_key
        try:
            resp = await http.get(f"{_BASE}/esummary.fcgi", params=params)
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
        except Exception:
            return None
        result = resp.json().get("result", {})
        gene = result.get(identifier)
        if not gene:
            return None
        return self._to_doc(identifier, gene)

    def _to_doc(self, gene_id: str, gene: dict) -> Document:
        description = gene.get("description", "")
        summary = gene.get("summary", "")
        organism = gene.get("organism", {})
        return Document(
            source_id=f"gene:{gene_id}",
            source_type="ncbi_gene",
            title=gene.get("name", gene.get("description", "")),
            abstract=summary or description,
            url=f"https://www.ncbi.nlm.nih.gov/gene/{gene_id}",
            metadata={
                "organism": organism.get("scientificname", ""),
                "chromosome": gene.get("chromosome", ""),
                "maplocation": gene.get("maplocation", ""),
                "gene_type": gene.get("genetypeid", ""),
                "nomenclature_symbol": gene.get("nomenclaturesymbol", ""),
            },
        )
