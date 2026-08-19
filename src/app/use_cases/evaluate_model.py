"""Use case: evaluate a single model against a single prompt."""

from __future__ import annotations

import time

import httpx

from src.domain.models import EvaluationResult, EvaluationScore
from src.domain.ports import LLMClientPort, LLMJudgePort, ResourceMonitorPort


class EvaluateModelUseCase:
    """Orchestrates one full evaluation run for a model/prompt pair.

    The use case only depends on ports, so it is decoupled from any
    concrete infrastructure (Hexagonal Architecture, application layer).

    Attributes:
        _client: Adapter that generates model responses.
        _judge: Adapter that scores responses.
        _monitor: Adapter that tracks resource usage.
    """

    def __init__(
        self,
        client: LLMClientPort,
        judge: LLMJudgePort,
        monitor: ResourceMonitorPort,
    ) -> None:
        """Initialize the use case with its dependencies.

        Args:
            client: LLM client used to generate responses.
            judge: LLM judge used to score responses.
            monitor: Resource monitor for hardware metrics.
        """
        self._client = client
        self._judge = judge
        self._monitor = monitor

    def execute(self, model_name: str, prompt: str) -> EvaluationResult:
        """Run the full evaluation pipeline.

        Steps:
            1. Start resource monitoring.
            2. Time the generation and receive the response.
            3. Stop monitoring and collect resource metrics.
            4. Send the prompt/response pair to the judge.
            5. Return an aggregated EvaluationResult.

        Args:
            model_name: Name of the model under evaluation.
            prompt: The test prompt to send to the model.

        Returns:
            An EvaluationResult containing the response, timing, resource
            usage, and judge score.
        """
        self._monitor.start_recording()

        start_time = time.perf_counter()
        response: str = self._client.generate_response(prompt)
        end_time = time.perf_counter()

        resources = self._monitor.stop_recording()

        score: EvaluationScore | None = None
        try:
            score = self._judge.evaluate_response(prompt, response)
        except (httpx.HTTPError, RuntimeError, ValueError):
            # Judge failures should not discard the run's other metrics.
            score = None

        return EvaluationResult(
            model_name=model_name,
            prompt=prompt,
            response=response,
            ttft_sec=0.0,  # Populated by streaming-capable adapters.
            total_time_sec=round(end_time - start_time, 3),
            resources=resources,
            score=score,
        )
