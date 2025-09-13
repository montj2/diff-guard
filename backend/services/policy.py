"""Policy engine skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(slots=True)
class PolicyDecision:
    action: str
    reason: str


class PolicyEngine:
    """Evaluate score + flags to produce a decision.

    Placeholder rules; real one will load YAML and severity mapping.
    """

    def decide(self, score: int | None, flags: Sequence[str]) -> PolicyDecision:  # pragma: no cover - simple logic
        if score is None:
            return PolicyDecision(action="quarantine", reason="missing_score")
        if any(f in {"adds_network_calls", "uses_eval", "obfuscation"} for f in flags):
            return PolicyDecision(action="quarantine", reason="critical_flag")
        if score >= 90:
            return PolicyDecision(action="promote", reason="high_score")
        return PolicyDecision(action="quarantine", reason="default")


__all__ = ["PolicyEngine", "PolicyDecision"]
