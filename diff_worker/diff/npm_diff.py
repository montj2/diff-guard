"""npm diff stub implementation."""

from __future__ import annotations


def generate_npm_diff(prev: str, new: str) -> str:  # pragma: no cover - stub
    """Return a placeholder diff string.

    Args:
        prev: Previous version identifier.
        new: New version identifier.
    """
    return f"--- a/{prev}\n+++ b/{new}\n@@ stub @@\n+placeholder change\n"
