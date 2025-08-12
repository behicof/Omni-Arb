"""Adaptor for FinGPT sentiment signal (stub implementation)."""
from __future__ import annotations

from typing import Dict, Any


def compute(market: str, timestamp: int) -> Dict[str, Any]:
    """Return a placeholder sentiment signal.

    Parameters
    ----------
    market: str
        Market name such as ``BTC/USDT``.
    timestamp: int
        Unix timestamp of the observation.
    """

    return {"signal": "flat", "strength": 0.0, "meta": {"source": "FinGPT"}}
