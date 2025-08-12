"""Generate natural language PnL and risk summaries.

This module provides a light‑weight adaptor inspired by FinGPT that
summarises trading performance and risk metrics into plain English.
The goal is not to implement a full large language model but to offer
clear, human readable explanations that can be easily unit tested.
"""
from __future__ import annotations

from datetime import date
from typing import Dict, Iterable


def _format_currency(value: float) -> str:
    """Return ``value`` formatted as a currency string."""

    return f"$ {value:,.2f}"

def _format_currency(value: float, currency_symbol: str = "$") -> str:
    """Return ``value`` formatted as a currency string.

    Parameters
    ----------
    value : float
        The numeric value to format.
    currency_symbol : str, optional
        The symbol to use for the currency (default is "$").
    """
    return f"{currency_symbol} {value:,.2f}"
def generate_report(pnl_rollup: Dict[date, float], risk: Dict[str, float]) -> str:
    """Create a natural‑language report for PnL and risk metrics.

    Parameters
    ----------
    pnl_rollup:
        Mapping from ``datetime.date`` to the realised PnL for that day.
    risk:
        Mapping of risk metric names to their values.  Typical entries might
        include things like ``max_drawdown`` or ``sharpe``.

    Returns
    -------
    str
        A human friendly report describing the supplied metrics.
    """

    if not pnl_rollup:
        pnl_text = "No trading activity was recorded."
    else:
        total = sum(pnl_rollup.values())
        best_day, best_pnl = max(pnl_rollup.items(), key=lambda x: x[1])
        worst_day, worst_pnl = min(pnl_rollup.items(), key=lambda x: x[1])
        pnl_text = (
            f"Total funding PnL over the period was {_format_currency(total)}. "
            f"The best day was {best_day.isoformat()} with a PnL of {_format_currency(best_pnl)}. "
            f"The worst day was {worst_day.isoformat()} with a PnL of {_format_currency(worst_pnl)}."
        )

    if risk:
        risk_parts = [f"{name.replace('_', ' ')} was {value:.2f}" for name, value in risk.items()]
        risk_text = " Key risk metrics: " + ", ".join(risk_parts) + "."
    else:
        risk_text = ""

    return pnl_text + risk_text
