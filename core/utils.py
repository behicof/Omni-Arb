import math


def net_edge_bps(long_bps: float, short_bps: float) -> float:
    """Return net edge in basis points as the difference between long and short yields."""
    return long_bps - short_bps


def basis_bps(spot: float, future: float) -> float:
    """Return the basis between futures and spot in basis points."""
    return ((future - spot) / spot) * 10000


def qty_from_notional(notional: float, price: float, lot: float) -> float:
    """Calculate trade quantity from notional value rounded down to lot size."""
    qty = notional / price
    steps = math.floor(qty / lot)
    return round(steps * lot, 10)
