"""Skeleton worker module for DiffGuard.

Will later orchestrate: fetch tarballs -> diff -> normalize -> heuristics -> LLM -> policy -> persistence.
"""

from __future__ import annotations

from typing import Any


def process_artifact(spec: dict[str, Any]) -> None:
    """Process a single artifact specification (placeholder).

    Args:
        spec: Artifact metadata dictionary.
    """
    # TODO: implement worker pipeline
    return None


def main() -> None:  # pragma: no cover - manual run path
    print("DiffGuard worker starting (skeleton)...")
    # TODO: implement queue consumption loop


if __name__ == "__main__":  # pragma: no cover
    main()
