"""DataSource abstract base class."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from open_synthesis.types import Document


class DataSource(ABC):
    """Base class for all data source integrations.

    Subclasses implement async search() and fetch() against a specific API.
    """

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    @staticmethod
    @abstractmethod
    def info() -> dict[str, Any]:
        """Return metadata about this source (description, auth_required, data_type)."""
        ...

    @abstractmethod
    async def search(self, query: str, max_results: int = 20) -> list[Document]:
        """Search the data source and return documents."""
        ...

    @abstractmethod
    async def fetch(self, identifier: str) -> Document | None:
        """Fetch a single document by its identifier (DOI, ID, etc.)."""
        ...
