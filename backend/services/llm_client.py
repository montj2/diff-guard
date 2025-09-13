"""LLM client skeleton."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScoringResult:
    score: int | None
    flags: list[str]
    reasoning: str


class LlmClient:
    """Stub LLM client returning a fixed result.

    Real implementation will call provider API with retries & JSON validation.
    """

    def score_diff(
        self,
        diff: str,
        package: dict[str, str],
        heuristics: dict[str, int],
    ) -> ScoringResult:  # pragma: no cover
        return ScoringResult(score=95, flags=[], reasoning="stub")


__all__ = ["LlmClient", "ScoringResult"]
