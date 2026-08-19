"""Ollama client adapter for local LLM inference via its REST API."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx

from src.domain.ports import LLMClientPort


class OllamaClientAdapter(LLMClientPort):
    """Adapter that calls a locally running Ollama server.

    Uses streaming so the response can be read incrementally; it is
    fully assembled before being returned.

    Attributes:
        model_name: Name of the Ollama model tag (e.g. 'llama3.2:1b').
        base_url: Base URL of the Ollama API.
    """

    def __init__(
        self,
        model_name: str,
        base_url: str | None = None,
        timeout: float = 120.0,
    ) -> None:
        """Initialize the adapter.

        Args:
            model_name: The model tag as registered in Ollama.
            base_url: The base URL of the Ollama API.
            timeout: HTTP request timeout in seconds.
        """
        self.model_name = model_name
        self.base_url = base_url or os.environ.get(
            "OLLAMA_BASE_URL", "http://localhost:11434"
        )
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"), timeout=timeout
        )

    def generate_response(self, prompt: str) -> str:
        """Send a prompt to Ollama and return the generated response.

        Args:
            prompt: The input text prompt.

        Returns:
            The concatenated response text from the model.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        payload: dict[str, Any] = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": True,
        }
        response_parts: list[str] = []
        with self._client.stream(
            "POST", "/api/generate", json=payload
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                response_parts.append(chunk.get("response", ""))
                if chunk.get("done", False):
                    break
        return "".join(response_parts)

    def __del__(self) -> None:
        """Close the underlying HTTP client."""
        if hasattr(self, "_client"):
            self._client.close()
