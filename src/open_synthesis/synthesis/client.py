"""RunPod serverless API client."""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from open_synthesis.config import RunPodSettings

_RUNPOD_BASE = "https://api.runpod.ai/v2"


class RunPodClient:
    """Async client for RunPod serverless inference endpoints."""

    def __init__(self, settings: RunPodSettings) -> None:
        self.endpoint_id = settings.endpoint_id
        self.api_key = settings.api_key
        self.timeout = settings.timeout
        self._client: httpx.AsyncClient | None = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=float(self.timeout),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def runsync(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Submit a synchronous inference request and wait for result."""
        http = await self._http()
        resp = await http.post(
            f"{_RUNPOD_BASE}/{self.endpoint_id}/runsync",
            json={"input": payload},
        )
        resp.raise_for_status()
        result = resp.json()
        if result.get("status") == "FAILED":
            raise RuntimeError(f"RunPod job failed: {result.get('error', 'unknown')}")
        if "output" not in result:
            raise RuntimeError(f"RunPod unexpected response: {result}")
        return result["output"]

    async def run_async(self, payload: dict[str, Any]) -> str:
        """Submit an async job and return the job ID."""
        http = await self._http()
        resp = await http.post(
            f"{_RUNPOD_BASE}/{self.endpoint_id}/run",
            json={"input": payload},
        )
        resp.raise_for_status()
        return resp.json()["id"]

    async def poll(self, job_id: str, interval: float = 2.0) -> dict[str, Any]:
        """Poll for async job completion."""
        http = await self._http()
        while True:
            resp = await http.get(f"{_RUNPOD_BASE}/{self.endpoint_id}/status/{job_id}")
            resp.raise_for_status()
            data = resp.json()
            status = data.get("status")
            if status == "COMPLETED":
                return data["output"]
            if status == "FAILED":
                raise RuntimeError(f"RunPod job {job_id} failed: {data.get('error', 'unknown')}")
            await asyncio.sleep(interval)

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
