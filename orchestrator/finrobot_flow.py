"""Simplified agent orchestration pipeline."""
from dataclasses import dataclass
from typing import Optional

from core.execution.funding_arb import FundingArb, FundingArbConfig
from core.risk.sizing import size_position


@dataclass
class Opportunity:
    edge: float
    price: float


@dataclass
class RiskLimits:
    max_notional: float
    margin_buffer: float


def process_opportunity(opp: Opportunity, limits: RiskLimits, arb: Optional[FundingArb] = None) -> float:
    """Return order size if opportunity passes funding arb filter."""
    arb = arb or FundingArb(FundingArbConfig(theta=0))
    if not arb.should_enter(opp.edge, 0, 0, 0):
        return 0.0
    return size_position(limits.max_notional, opp.price, limits.margin_buffer)
