"""PubChem PUG REST API integration."""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"


class PubChemSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "Chemical compound data and descriptions from PubChem",
            "auth_required": False,
            "data_type": "chemical",
            "rate_limit": "5 requests/sec",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        encoded = quote(query, safe="")

        # Get CIDs by compound name
        try:
            resp = await http.get(f"{_BASE}/compound/name/{encoded}/cids/JSON")
            if resp.status_code != 200:
                return []
            cids = resp.json().get("IdentifierList", {}).get("CID", [])
        except Exception:
            return []

        cids = cids[:max_results]
        if not cids:
            return []

        # Get descriptions for found CIDs
        cid_str = ",".join(str(c) for c in cids)
        try:
            desc_resp = await http.get(f"{_BASE}/compound/cid/{cid_str}/description/JSON")
            if desc_resp.status_code != 200:
                return [self._minimal_doc(c) for c in cids]
            descriptions = desc_resp.json().get("InformationList", {}).get("Information", [])
        except Exception:
            return [self._minimal_doc(c) for c in cids]

        # Group descriptions by CID
        by_cid: dict[int, list[dict]] = {}
        for info in descriptions:
            cid = info.get("CID")
            if cid:
                by_cid.setdefault(cid, []).append(info)

        docs = []
        for cid in cids:
            infos = by_cid.get(cid, [])
            docs.append(self._info_to_doc(cid, infos))
        return docs

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        try:
            resp = await http.get(f"{_BASE}/compound/cid/{identifier}/description/JSON")
            if resp.status_code == 404:
                return None
            if resp.status_code != 200:
                return None
            infos = resp.json().get("InformationList", {}).get("Information", [])
        except Exception:
            return None

        if not infos:
            return self._minimal_doc(int(identifier))

        return self._info_to_doc(int(identifier), infos)

    def _info_to_doc(self, cid: int, infos: list[dict]) -> Document:
        title = ""
        desc_parts = []
        sources = []

        for info in infos:
            if not title:
                title = info.get("Title", "")
            desc = info.get("Description", "")
            if desc:
                source = info.get("DescriptionSourceName", "")
                desc_parts.append(desc)
                if source:
                    sources.append(source)

        return Document(
            source_id=f"pubchem:{cid}",
            source_type="pubchem",
            title=title or f"CID {cid}",
            abstract="\n\n".join(desc_parts) if desc_parts else None,
            url=f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
            metadata={
                "cid": cid,
                "description_sources": sources,
            },
        )

    def _minimal_doc(self, cid: int) -> Document:
        return Document(
            source_id=f"pubchem:{cid}",
            source_type="pubchem",
            title=f"CID {cid}",
            url=f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
        )
