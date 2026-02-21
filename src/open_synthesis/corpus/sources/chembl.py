"""ChEMBL API integration."""

from __future__ import annotations

import json
from typing import Any

from open_synthesis.corpus.base import DataSource
from open_synthesis.types import Document

_BASE = "https://www.ebi.ac.uk/chembl/api/data"


class ChemblSource(DataSource):
    @staticmethod
    def info() -> dict[str, Any]:
        return {
            "description": "ChEMBL bioactivity and drug compound data",
            "auth_required": False,
            "data_type": "chemistry",
            "rate_limit": "No published limit",
        }

    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        http = await self.client()
        resp = await http.get(
            f"{_BASE}/molecule/search.json",
            params={"q": query, "limit": max_results},
        )
        if resp.status_code != 200:
            return []
        molecules = resp.json().get("molecules", [])
        return [self._mol_to_doc(m) for m in molecules]

    async def fetch(self, identifier: str) -> Document | None:
        http = await self.client()
        resp = await http.get(f"{_BASE}/molecule/{identifier}.json")
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        mol = resp.json()
        doc = self._mol_to_doc(mol)
        props = mol.get("molecule_properties", {})
        if props:
            doc.full_text = json.dumps(props, indent=2)
        return doc

    def _mol_to_doc(self, mol: dict) -> Document:
        chembl_id = mol.get("molecule_chembl_id", "")
        pref_name = mol.get("pref_name", "") or chembl_id
        props = mol.get("molecule_properties", {}) or {}
        return Document(
            source_id=f"chembl:{chembl_id}",
            source_type="chembl",
            title=pref_name,
            abstract=f"{pref_name} — {mol.get('molecule_type', 'unknown type')}, max phase {mol.get('max_phase', 'N/A')}",
            metadata={
                "chembl_id": chembl_id,
                "molecule_type": mol.get("molecule_type", ""),
                "max_phase": mol.get("max_phase"),
                "full_mwt": props.get("full_mwt", ""),
                "alogp": props.get("alogp", ""),
            },
        )
