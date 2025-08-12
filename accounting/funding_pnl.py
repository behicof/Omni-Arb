"""Utilities for computing funding payment PnL.

This module provides helper data structures and functions for
calculating funding payment profit and loss over configurable
windows and for rolling the results up on a daily basis.

The implementation avoids heavy dependencies so it can operate on
simple Python data structures.  Funding payments are represented
via the :class:`FundingRecord` data class.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Iterable, List, Dict, Any


@dataclass
class FundingRecord:
    """Single funding payment.

    Attributes
    ----------
    timestamp: datetime
        Time at which the funding payment was applied.
    rate: float
        Funding rate for the period expressed as a decimal.  A value of
        ``0.001`` corresponds to 0.1%.
    position: float
        Position size in base currency.  Positive values represent long
        positions and negative values represent short positions.
    price: float
        Mark price of the asset at ``timestamp``.
    """

    timestamp: datetime
    rate: float
    position: float
    price: float

    @property
    def pnl(self) -> float:
        """Return the funding PnL for this record.

        The PnL is computed as ``position * price * rate`` which mirrors the
        common calculation for perpetual swap exchanges.
        """

        return self.position * self.price * self.rate


def windowed_funding_pnl(
    records: Iterable[FundingRecord],
    window: timedelta,
) -> List[Dict[str, Any]]:
    """Aggregate funding PnL over fixed windows.

    Parameters
    ----------
    records:
        Iterable of :class:`FundingRecord` objects.  They need not be sorted;
        the function will process them in chronological order.
    window:
        Size of the aggregation window.  Windows are created sequentially
        starting from the timestamp of the first record.

    Returns
    -------
    list of dict
        Each element contains ``start`` (datetime), ``end`` (datetime) and
        ``pnl`` (float) fields describing the PnL accumulated over that
        interval.
    """

    # Sort records by timestamp to ensure chronological processing
    sorted_records = sorted(records, key=lambda r: r.timestamp)
    results: List[Dict[str, Any]] = []

    if not sorted_records:
        return results

    # Initialize the first window boundaries
    window_start = sorted_records[0].timestamp
    window_end = window_start + window
    pnl_accumulator = 0.0

    for record in sorted_records:
        # If the record falls outside the current window, close windows until
        # it fits in the active one
        while record.timestamp >= window_end:
            results.append(
                {
                    "start": window_start,
                    "end": window_end,
                    "pnl": pnl_accumulator,
                }
            )
            pnl_accumulator = 0.0
            window_start = window_end
            window_end = window_start + window

        pnl_accumulator += record.pnl

    # Append the final window
    results.append({"start": window_start, "end": window_end, "pnl": pnl_accumulator})

    return results


def daily_rollup(records: Iterable[FundingRecord]) -> Dict[date, float]:
    """Roll up funding PnL on a daily basis.

    The function aggregates funding PnL for each UTC day and returns a
    mapping from :class:`datetime.date` to the total PnL for that day.
    """

    day_pnl: Dict[date, float] = {}
    for window in windowed_funding_pnl(records, timedelta(days=1)):
        day = window["start"].date()
        day_pnl[day] = day_pnl.get(day, 0.0) + window["pnl"]
    return day_pnl
