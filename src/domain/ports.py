from __future__ import annotations

from abc import ABC, abstractmethod

from src.domain.models import EvaluationScore, ResourceUsageMetrics


class LLMClientPort(ABC):
    """Port for generating responses from an LLM."""

    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        """Generate a text response for the given prompt.

        Args:
            prompt: The input prompt string.

        Returns:
            The generated text response.
        """


class LLMJudgePort(ABC):
    """Port for evaluating an LLM response using an LLM-as-a-Judge."""

    @abstractmethod
    def evaluate_response(self, prompt: str, response: str) -> EvaluationScore:
        """Evaluate the quality of a response given the original prompt.

        Args:
            prompt: The original prompt sent to the model.
            response: The generated response to evaluate.

        Returns:
            An EvaluationScore with faithfulness, relevance, safety, and
            feedback.
        """


class ResourceMonitorPort(ABC):
    """Port for monitoring hardware resource usage during inference."""

    @abstractmethod
    def start_recording(self) -> None:
        """Begin recording resource usage metrics."""

    @abstractmethod
    def stop_recording(self) -> ResourceUsageMetrics:
        """Stop recording and return the collected metrics.

        Returns:
            A ResourceUsageMetrics snapshot with recorded RAM, VRAM, and
            CPU values.
        """
