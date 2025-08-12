"""Simple placeholder RL agent for testing purposes."""

from typing import Any, Dict


def act(state: Dict[str, Any]) -> Dict[str, Any]:
    """Return a dummy action."""
    return {"action": "hold"}
