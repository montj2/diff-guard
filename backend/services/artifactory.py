"""Artifactory client skeleton."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ArtifactRef:
    name: str
    version: str
    repo: str


class ArtifactoryClient:
    def __init__(self, base_url: str, token: str | None) -> None:  # pragma: no cover - trivial
        self._base_url = base_url.rstrip("/") if base_url else base_url
        self._token = token

    def promote(self, ref: ArtifactRef) -> bool:  # pragma: no cover - stub
        return True

    def quarantine(self, ref: ArtifactRef, reason: str) -> bool:  # pragma: no cover - stub
        return True


__all__ = ["ArtifactoryClient", "ArtifactRef"]
