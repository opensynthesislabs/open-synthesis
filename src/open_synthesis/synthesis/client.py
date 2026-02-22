"""vLLM inference client for RunPod GPU pods."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from open_synthesis.config import RunPodSettings


class RunPodClient:
    """Async client for vLLM running on a RunPod GPU pod.

    Connects to the OpenAI-compatible API exposed by vLLM at
    https://{pod_id}-8000.proxy.runpod.net/v1/chat/completions
    or a custom base URL (e.g. http://localhost:8000 via SSH tunnel).
    """

    MAX_CONTEXT_LEN = 32768  # Must match vLLM --max-model-len

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

    def _build_messages(self, prompt: str, context: str) -> list[dict[str, str]]:
        """Build the chat messages list from prompt and context."""
        return [
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

    def _clamp_max_tokens(
        self, messages: list[dict[str, str]], max_tokens: int,
    ) -> int:
        """Clamp max_tokens to fit within context window."""
        input_chars = sum(len(m["content"]) for m in messages)
        estimated_input_tokens = input_chars // 3  # conservative estimate
        available_for_output = self.MAX_CONTEXT_LEN - estimated_input_tokens
        if available_for_output < 256:
            raise ValueError(
                f"Input too long (~{estimated_input_tokens} tokens estimated). "
                f"Reduce retrieval results or context size."
            )
        return min(max_tokens, available_for_output)

    async def generate(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> str:
        """Send a chat completion request to vLLM and return the response text."""
        messages = self._build_messages(prompt, context)
        max_tokens = self._clamp_max_tokens(messages, max_tokens)

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
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )
        if resp.status_code != 200:
            detail = resp.text[:500]
            raise RuntimeError(f"vLLM returned {resp.status_code}: {detail}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    async def generate_stream(
        self,
        prompt: str,
        context: str,
        temperature: float = 0.3,
        max_tokens: int = 4096,
    ) -> AsyncIterator[str]:
        """Stream chat completion tokens from vLLM as an async iterator."""
        messages = self._build_messages(prompt, context)
        max_tokens = self._clamp_max_tokens(messages, max_tokens)

        http = await self._http()
        async with http.stream(
            "POST",
            f"{self._base_url}/v1/chat/completions",
            json={
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "top_p": 0.9,
                "repetition_penalty": 1.1,
                "stream": True,
                "chat_template_kwargs": {"enable_thinking": False},
            },
        ) as resp:
            if resp.status_code != 200:
                body = await resp.aread()
                raise RuntimeError(
                    f"vLLM returned {resp.status_code}: {body.decode()[:500]}"
                )
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:]
                if payload.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                    delta = chunk["choices"][0].get("delta", {})
                    content = delta.get("content")
                    if content:
                        yield content
                except (json.JSONDecodeError, KeyError, IndexError):
                    continue

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
