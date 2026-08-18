from __future__ import annotations
import re

INJECTION_PATTERNS = [
    r"ignore\s+(all|any|previous)\s+instructions",
    r"system\s+message",
    r"reveal\s+(your|the)\s+prompt",
    r"execute\s+(this|the)\s+command",
]


def sanitize_artifact(text: str) -> str:
    """Treat external artifacts as untrusted data, not instructions."""
    cleaned = text
    for pattern in INJECTION_PATTERNS:
        cleaned = re.sub(pattern, "[UNTRUSTED-INSTRUCTION-REMOVED]", cleaned, flags=re.I)
    return cleaned
