"""OpenAI judge adapter for LLM-as-a-Judge evaluation."""

from __future__ import annotations

import httpx
from openai import OpenAI

from src.infra.llm.judge.base_adapter import BaseJudgeAdapter


class OpenAIJudgeAdapter(BaseJudgeAdapter):
    """LLM-as-a-Judge adapter using OpenAI models."""

    def _call_api(self, prompt: str, response: str) -> str:
        client = OpenAI(api_key=self.api_key, timeout=30.0)

        try:
            result = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.JUDGE_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            f"Original prompt: {prompt}\n\n"
                            f"Generated response: {response}"
                        ),
                    },
                ],
            )
            return result.choices[0].message.content or ""
        except httpx.HTTPError as exc:
            raise RuntimeError(f"OpenAI judge HTTP error: {exc}") from exc
        except Exception as exc:
            raise RuntimeError(f"OpenAI judge API error: {exc}") from exc
