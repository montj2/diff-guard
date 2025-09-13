"""Red flag heuristic stubs."""

from __future__ import annotations

from collections import Counter

SUSPICIOUS_PATTERNS = {
    "eval(": "uses_eval",
    "http.request": "adds_network_calls",
    "https.request": "adds_network_calls",
    "child_process": "adds_network_calls",
    "require('crypto'": "crypto_addition",
    "atob(": "suspicious_encoding",
    "Buffer.from(": "suspicious_encoding",
}


def extract_heuristics(diff_text: str) -> dict[str, int]:  # pragma: no cover - stub
    counts: Counter[str] = Counter()
    for needle, flag in SUSPICIOUS_PATTERNS.items():
        if needle in diff_text:
            counts[flag] += diff_text.count(needle)
    return dict(counts)
