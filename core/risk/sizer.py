"""Simple position sizing utilities."""
from typing import Union


def fixed_fraction(notional: float, fraction: Union[int, float]) -> float:
    """Calculate position size as a fraction of notional value."""
    if fraction < 0:
        raise ValueError("fraction must be non-negative")
    return notional * float(fraction)
