"""GWAS Catalog API integration."""

from __future__ import annotations

from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://www.ebi.ac.uk/gwas/rest/api"


class GwasCatalogSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "NHGRI-EBI GWAS Catalog of genome-wide association studies",
            "auth_required": False,
            "data_type": "genomics",
            "rate_limit": "No formal limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        try:
            resp = await http.get(
                f"{_BASE}/studies/search/findByDiseaseTrait",
                params={"diseaseTrait": query, "page": 0, "size": max_results},
            )
            resp.raise_for_status()
        except Exception:
            return []
        studies = resp.json().get("_embedded", {}).get("studies", [])
        return [self._to_doc(s) for s in studies]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(f"{_BASE}/studies/{identifier}")
            if resp.status_code == 404:
                return None
            resp.raise_for_status()
        except Exception:
            return None
        return self._to_doc(resp.json())

    def _to_doc(self, study: dict) -> Document:
        accession = study.get("accessionId", "")
        pub = study.get("publicationInfo", {})
        author = pub.get("author", {})
        trait = study.get("diseaseTrait", {})
        pub_date = pub.get("publicationDate", "")
        year = int(pub_date[:4]) if pub_date and len(pub_date) >= 4 else None
        return Document(
            source_id=f"gwas:{accession}",
            source_type="gwas_catalog",
            title=pub.get("title", trait.get("trait", accession)),
            authors=[author.get("fullname", "")] if author.get("fullname") else [],
            year=year,
            abstract=trait.get("trait", ""),
            url=f"https://www.ebi.ac.uk/gwas/studies/{accession}",
            metadata={
                "accession_id": accession,
                "disease_trait": trait.get("trait", ""),
                "initial_sample_size": study.get("initialSampleSize", ""),
                "platform": study.get("platform", ""),
            },
        )
