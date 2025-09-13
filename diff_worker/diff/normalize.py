"""Diff normalization stub."""

from __future__ import annotations


def normalize_diff(diff_text: str, max_bytes: int = 200_000) -> str:  # pragma: no cover - stub
    if len(diff_text.encode("utf-8")) > max_bytes:
        return diff_text[: max_bytes // 2] + "\n...<truncated>...\n" + diff_text[-max_bytes // 2 :]
    return diff_text
