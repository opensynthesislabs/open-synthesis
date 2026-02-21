"""vLLM inference client for RunPod GPU pods."""

from __future__ import annotations

from typing import Any

import httpx

from open_synthesis.config import RunPodSettings


class RunPodClient:
    """Async client for vLLM running on a RunPod GPU pod.

    Connects to the OpenAI-compatible API exposed by vLLM at
    https://{pod_id}-8000.proxy.runpod.net/v1/chat/completions
    or a custom base URL (e.g. http://localhost:8000 via SSH tunnel).
    """

    MAX_CONTEXT_LEN = 8192  # Must match vLLM --max-model-len

    def __init__(self, settings: RunPodSettings) -> None:
        self.pod_id = settings.pod_id
        self.api_key = settings.api_key
        self.model = settings.model
        self.timeout = settings.timeout
        # Use base_url override if set, otherwise construct from pod_id.
        # Set RUNPOD_BASE_URL=http://localhost:8000 when using SSH tunnel.
        self._base_url = settings.base_url or f"https://{self.pod_id}-8000.proxy.runpod.net"
        self._client: httpx.AsyncClient | None = None

    async def _http(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=float(self.timeout),
                headers={"Content-Type": "application/json"},
            )
        return self._client

    async def generate(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat completion request to vLLM and return the response text."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a research synthesis tool. Synthesize the following "
                    "retrieved source material accurately and cite sources inline.\n\n"
                    f"<retrieved_sources>\n{context}\n</retrieved_sources>"
                ),
            },
            {"role": "user", "content": prompt},
        ]

        # Rough token estimate: ~4 chars per token. Reserve space for output.
        input_chars = sum(len(m["content"]) for m in messages)
        estimated_input_tokens = input_chars // 3  # conservative estimate
        available_for_output = self.MAX_CONTEXT_LEN - estimated_input_tokens
        if available_for_output < 256:
            raise ValueError(
                f"Input too long (~{estimated_input_tokens} tokens estimated). "
                f"Reduce retrieval results or context size."
            )
        max_tokens = min(max_tokens, available_for_output)

        http = await self._http()
        resp = await http.post(
            f"{self._base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
            },
        )
        if resp.status_code != 200:
            detail = resp.text[:500]
            raise RuntimeError(f"vLLM returned {resp.status_code}: {detail}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def runsync(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Legacy-compatible interface used by the pipeline."""
        text = await self.generate(
            prompt=payload.get("prompt", ""),
            context=payload.get("context", ""),
            temperature=payload.get("temperature", 0.3),
            max_tokens=payload.get("max_new_tokens", 4096),
        )
        return {"synthesis": text}

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()
