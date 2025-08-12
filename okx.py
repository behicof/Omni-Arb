"""OKX REST helper for demo/live trading header."""

from __future__ import annotations
from typing import Dict


def build_headers(demo: bool = True) -> Dict[str, str]:
    """Return headers for OKX; add x-simulated-trading for demo mode."""
    headers: Dict[str, str] = {}
    if demo:
        headers["x-simulated-trading"] = "1"
    return headers
