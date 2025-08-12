"""Command-line runner for walk-forward validation.

Reads a CSV file containing three columns: ``start``, ``t1`` and ``return``.
The data must be ordered by ``start`` in ascending order.

The script evaluates out-of-sample performance using :class:`PurgedKFold`
validation. For each fold the following metrics are reported:

* Sharpe ratio
* Maximum drawdown
* Return variance
"""

from __future__ import annotations

import argparse
import csv
import math
from typing import Dict, Iterable, List

from .purged_kfold import PurgedKFold


def sharpe_ratio(returns: Iterable[float]) -> float:
    ret_list = list(returns)
    n = len(ret_list)
    if n == 0:
        return 0.0
    mean = sum(ret_list) / n
    var = sum((r - mean) ** 2 for r in ret_list) / n
    std = math.sqrt(var)
    return 0.0 if std == 0 else mean / std * math.sqrt(periods_per_year)


def max_drawdown(returns: Iterable[float]) -> float:
    cum = 1.0
    peak = 1.0
    max_dd = 0.0
    for r in returns:
        cum *= 1.0 + r
        if cum > peak:
            peak = cum
        dd = cum / peak - 1.0
        if dd < max_dd:
            max_dd = dd
    return max_dd


def variance(returns: Iterable[float]) -> float:
    ret_list = list(returns)
    n = len(ret_list)
    if n == 0:
        return 0.0
    mean = sum(ret_list) / n
    return sum((r - mean) ** 2 for r in ret_list) / n


def run_wfo(
    data: Iterable[Dict[str, float]], n_splits: int = 5, embargo_pct: float = 0.0
) -> List[Dict[str, float]]:
    """Run walk-forward validation over ``data``.

    Parameters
    ----------
    data : iterable of dict
        Each element must contain ``start``, ``t1`` and ``return`` keys.
    n_splits : int, optional
        Number of folds.
    embargo_pct : float, optional
        Fraction of observations to embargo around each test fold.
    """

    rows = list(data)
    starts = [row["start"] for row in rows]
    t1 = [row["t1"] for row in rows]
    returns = [row["return"] for row in rows]

    pkf = PurgedKFold(n_splits=n_splits, embargo_pct=embargo_pct)
    results: List[Dict[str, float]] = []
    for i, (_, test_idx) in enumerate(pkf.split(starts, t1), start=1):
        test_returns = [returns[j] for j in test_idx]
        metrics = {
            "fold": float(i),
            "sharpe": sharpe_ratio(test_returns),
            "maxdd": max_drawdown(test_returns),
            "variance": variance(test_returns),
        }
        results.append(metrics)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward validation runner")
    parser.add_argument("csv", help="CSV file with columns start,t1,return")
    parser.add_argument("--splits", type=int, default=5, help="Number of folds")
    parser.add_argument(
        "--embargo",
        type=float,
        default=0.0,
        help="Embargo percentage to remove observations around test fold",
    )
    args = parser.parse_args()

    with open(args.csv, "r", newline="") as f:
        reader = csv.DictReader(f)
        data = [
            {
                "start": float(row["start"]),
                "t1": float(row["t1"]),
                "return": float(row["return"]),
            }
            for row in reader
        ]

    results = run_wfo(data, n_splits=args.splits, embargo_pct=args.embargo)

    print(f"{'fold':<5}{'sharpe':>10}{'maxdd':>10}{'variance':>10}")
    for row in results:
        print(
            f"{int(row['fold']):<5}{row['sharpe']:>10.4f}{row['maxdd']:>10.4f}{row['variance']:>10.4f}"
        )


if __name__ == "__main__":
    main()
