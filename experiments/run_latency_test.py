"""Composition Root - wires adapters and runs the evaluation pipeline."""

from __future__ import annotations

import os
from typing import Literal

import httpx

from src.app.use_cases.evaluate_model import EvaluateModelUseCase
from src.domain.models import EvaluationResult
from src.domain.ports import LLMClientPort, LLMJudgePort, ResourceMonitorPort
from src.infra.llm.judge.gemini_adapter import GeminiJudgeAdapter
from src.infra.llm.judge.openai_adapter import OpenAIJudgeAdapter
from src.infra.llm.ollama_adapter import OllamaClientAdapter
from src.infra.monitoring.system_monitor_adapter import SystemMonitorAdapter

# Test prompts about supporting diabetes patients.
TEST_PROMPTS: list[str] = [
    "What are the early symptoms of type 2 diabetes I should watch for?",
    # "How can I manage my blood sugar levels through diet and exercise?",
    # "What is the difference between type 1 and type 2 diabetes?",
]

# Models to evaluate - adjust tags to your local Ollama installation.
MODEL_NAMES: list[str] = [
    # "llama3.2:1b",
    # "gemma2:2b",
    # "phi3:mini",
    "mistral",
    # "qwen2.5:0.5b",
]

JudgeType = Literal["openai", "gemini-flash", "gemini-pro"]


def build_judge(judge_type: JudgeType) -> LLMJudgePort:
    """Factory: creates a configured LLM Judge adapter based on selected provider/model.

    Encapsulates rate-limiting delays so main execution loop stays clean.
    """
    if judge_type == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")
        return OpenAIJudgeAdapter(
            model="gpt-4o-mini",
            api_key=api_key,
            rate_limit_delay_sec=30,
        )

    elif judge_type == "gemini-flash":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        return GeminiJudgeAdapter(
            model="gemini-3.6-flash",
            api_key=api_key,
            rate_limit_delay_sec=30,
        )

    elif judge_type == "gemini-pro":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")
        return GeminiJudgeAdapter(
            model="gemini-3.1-pro-preview",
            api_key=api_key,
            rate_limit_delay_sec=60,
        )

    else:
        raise ValueError(f"Unknown judge_type: {judge_type}")


def build_client(model_name: str) -> LLMClientPort:
    """Factory: create an Ollama-backed client for a model.

    Args:
        model_name: The Ollama model tag.

    Returns:
        A configured OllamaClientAdapter.
    """
    return OllamaClientAdapter(model_name=model_name)


def build_monitor() -> ResourceMonitorPort:
    """Factory: create the system resource monitor.

    Returns:
        A SystemMonitorAdapter.
    """
    return SystemMonitorAdapter()


def main() -> None:
    """Run the evaluation across every model/prompt combination."""
    monitor: ResourceMonitorPort = build_monitor()
    selected_judge: JudgeType = "gemini-flash"
    judge: LLMJudgePort = build_judge(selected_judge)
    results: list[EvaluationResult] = []

    for model_name in MODEL_NAMES:
        use_case = EvaluateModelUseCase(
            client=build_client(model_name), judge=judge, monitor=monitor
        )

        print(f"Warming up '{model_name}'...")
        use_case.execute(model_name, "Hello")

        for prompt in TEST_PROMPTS:
            print(f"\nEvaluating '{model_name}' | '{prompt[:60]}...'")
            try:
                result = use_case.execute(model_name, prompt)
                results.append(result)
                print(f"  response_len={len(result.response)}")
                print(f"  total_time={result.total_time_sec:.3f}s")
                print(f"  ram_peak={result.resources.ram_used_mb:.2f}MB")
                print(f"  vram_peak={result.resources.vram_used_mb:.2f}MB")
                print(f"  cpu_avg={result.resources.cpu_percent:.2f}%")
                if result.score is not None:
                    print(
                        f"  faithfulness={result.score.faithfulness_score:.2f} "
                        f"relevance={result.score.relevance_score:.2f} "
                        f"safety={'PASS' if result.score.safety_passed else 'FAIL'}"
                    )
                    print(f"  feedback={result.score.feedback}")
            except (RuntimeError, ValueError, httpx.HTTPError) as exc:
                print(f"  ERROR: {exc}")

    print(f"\nCompleted {len(results)} evaluation(s).")


if __name__ == "__main__":
    main()
