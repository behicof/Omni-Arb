"""Core financial calculation helpers."""
from __future__ import annotations
import math


def basis_bps(spot: float, future: float) -> float:
    """Return basis in basis points between future and spot."""
    if spot <= 0:
        raise ValueError("spot must be positive")
    return (future - spot) / spot * 10_000


def net_edge_bps(spot: float, future: float, costs_bps: float = 0.0) -> float:
    """Basis minus execution and funding costs.

    Parameters
    ----------
    spot: float
        Spot price reference.
    future: float
        Futures price reference.
    costs_bps: float, optional
        Combined trading costs in basis points.
    """
    return basis_bps(spot, future) - costs_bps


def qty_from_notional(notional: float, price: float, lot: float) -> float:
    """Convert notional value to quantity rounded down to lot size."""
    if price <= 0 or lot <= 0:
        raise ValueError("price and lot must be positive")
    raw_qty = notional / price
    lots = math.floor(raw_qty / lot)
    return lots * lot
