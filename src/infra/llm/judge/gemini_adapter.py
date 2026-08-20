"""Gemini judge adapter for LLM-as-a-Judge evaluation."""

from __future__ import annotations

import httpx
from google import genai
from google.genai import types as genai_types

from src.infra.llm.judge.base_adapter import BaseJudgeAdapter


class GeminiJudgeAdapter(BaseJudgeAdapter):
    """LLM-as-a-Judge adapter using Google Gemini models."""

    def _call_api(self, prompt: str, response: str) -> str:
        client = genai.Client(
            api_key=self.api_key,
            http_options=genai_types.HttpOptions(timeout=30000),
        )
        judge_prompt = (
            f"{self.JUDGE_SYSTEM_PROMPT}\n\n"
            f"Original prompt: {prompt}\n\n"
            f"Generated response: {response}"
        )

        try:
            result = client.models.generate_content(
                model=self.model,
                contents=judge_prompt,
            )
            return result.text or ""
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Gemini judge HTTP error: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"Gemini judge API error: {exc}") from exc
