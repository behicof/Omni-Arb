"""Placeholder reinforcement learning trading agent.

The real project is expected to integrate a sophisticated RL based
policy.  For the purposes of the unit tests in this kata we only need
basic scaffolding so the module can be imported.
"""
from __future__ import annotations

from typing import Dict, Any


def decide(signal: Dict[str, Any], risk: Dict[str, Any]) -> Dict[str, Any]:
    """Return a stub trading decision.

    The function simply returns a 'hold' decision.  It mirrors the
    interface expected by :class:`base.Policy`.
    """

    return {"action": "hold", "size": 0.0, "leverage": 1}
