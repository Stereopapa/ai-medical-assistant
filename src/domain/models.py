"""Core immutable data structures for the LLM evaluation module."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationScore:
    """Immutable score assigned by an LLM Judge to a response.

    Attributes:
        faithfulness_score: Factual accuracy score (0.0-1.0).
        relevance_score: Relevance to the original prompt (0.0-1.0).
        safety_passed: Whether the response passed safety checks.
        feedback: Qualitative feedback from the judge.
    """

    faithfulness_score: float
    relevance_score: float
    safety_passed: bool
    feedback: str


@dataclass(frozen=True)
class ResourceUsageMetrics:
    """Immutable snapshot of hardware resource usage during inference.

    Attributes:
        ram_used_mb: Peak RAM usage in megabytes.
        vram_used_mb: Peak VRAM usage in megabytes.
        cpu_percent: Average CPU utilization percentage.
    """

    ram_used_mb: float
    vram_used_mb: float
    cpu_percent: float


@dataclass(frozen=True)
class EvaluationResult:
    """Immutable aggregated result of a single model evaluation run.

    Attributes:
        model_name: Name of the evaluated model.
        prompt: The input prompt sent to the model.
        response: The model's generated response.
        ttft_sec: Time to first token in seconds.
        total_time_sec: Total execution time in seconds.
        resources: Resource usage metrics collected during inference.
        score: Optional evaluation score assigned by the judge.
    """

    model_name: str
    prompt: str
    response: str
    ttft_sec: float
    total_time_sec: float
    resources: ResourceUsageMetrics
    score: EvaluationScore | None
