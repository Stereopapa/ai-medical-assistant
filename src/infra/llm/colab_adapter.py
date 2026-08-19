"""Adapter for LLMs served from a Google Colab tunnel/endpoint."""

from __future__ import annotations

from typing import Any

import httpx

from src.domain.ports import LLMClientPort


class ColabLLMAdapter(LLMClientPort):
    """Adapter that calls a model served from a Colab endpoint.

    Colab setups typically expose a Gradio/ngrok/tunnel HTTP endpoint
    that accepts a JSON body containing a 'prompt' field.

    Attributes:
        endpoint_url: Full URL of the Colab-served endpoint.
    """

    def __init__(self, endpoint_url: str, timeout: float = 120.0) -> None:
        """Initialize the adapter.

        Args:
            endpoint_url: Full URL of the Colab-served endpoint.
            timeout: HTTP request timeout in seconds.
        """
        self.endpoint_url = endpoint_url
        self._client = httpx.Client(timeout=timeout)

    def generate_response(self, prompt: str) -> str:
        """Send a prompt to the Colab endpoint and return the response.

        Args:
            prompt: The input text prompt.

        Returns:
            The generated response text.

        Raises:
            httpx.HTTPError: If the HTTP request fails.
        """
        payload: dict[str, Any] = {"prompt": prompt}
        response = self._client.post(self.endpoint_url, json=payload)
        response.raise_for_status()
        data = response.json()
        # Support several common response-field conventions.
        return str(
            data.get("response")
            or data.get("text")
            or data.get("output")
            or ""
        )

    def __del__(self) -> None:
        """Close the underlying HTTP client."""
        if hasattr(self, "_client"):
            self._client.close()
