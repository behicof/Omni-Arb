"""High-Confidence Off-Policy Evaluation (HCOPE) utilities.

This module provides helpers to compute a lower confidence bound (LCB)
for policy performance metrics and a gate function that checks whether a
policy meets a minimum expected performance threshold before live
execution.
"""
from __future__ import annotations

from scipy.stats import norm


def calculate_lcb(estimated_metric: float, estimated_std: float, confidence_level: float = 0.95) -> float:
    """Calculate the lower confidence bound for an estimated metric.

    Args:
        estimated_metric: Estimated value of the metric (e.g. Sharpe ratio).
        estimated_std: Standard deviation of the metric estimate.
        confidence_level: Confidence level for the bound (default 95%).

    Returns:
        The lower confidence bound of the metric.
    """
    if estimated_std < 0:
        raise ValueError("estimated_std must be non-negative")
    if not (0 < confidence_level < 1):
        raise ValueError("confidence_level must be between 0 and 1")
    z_score = norm.ppf(confidence_level)
    return estimated_metric - z_score * estimated_std


def evaluate_policy_performance(
    estimated_sharpe: float, estimated_std_sharpe: float, confidence_level: float = 0.95
) -> float:
    """Evaluate policy performance using the lower confidence bound of Sharpe ratio.

    The calculated bound is printed for visibility when running experiments or
    backtests so users can quickly inspect the conservative estimate.

    Args:
        estimated_sharpe: Estimated Sharpe ratio of the policy.
        estimated_std_sharpe: Standard deviation of the Sharpe ratio estimate.
        confidence_level: Confidence level for the bound (default 95%).

    Returns:
        The lower confidence bound of the Sharpe ratio.
    """
    lcb = calculate_lcb(estimated_sharpe, estimated_std_sharpe, confidence_level)
    print(f"Lower confidence bound (LCB) for Sharpe ratio: {lcb}")
    return lcb


def hcope_gate(
    sharpe_ratio: float,
    sharpe_std: float,
    threshold: float = 1.0,
    confidence_level: float = 0.95,
) -> bool:
    """Check if a policy passes the HCOPE gate.

    The gate passes when the lower confidence bound (LCB) of the Sharpe ratio
    is greater than or equal to the provided threshold.  By default the
    threshold is set to ``1.0`` which requires the policy to have a
    risk-adjusted return better than a ``1`` Sharpe ratio before execution.

    Args:
        sharpe_ratio: Estimated Sharpe ratio of the policy.
        sharpe_std: Standard deviation of the Sharpe ratio estimate.
        threshold: Minimum acceptable lower confidence bound (default ``1.0``).
        confidence_level: Confidence level for the bound (default 95%).

    Returns:
        ``True`` if the policy passes the gate, ``False`` otherwise.
    """
    lcb_sharpe = evaluate_policy_performance(sharpe_ratio, sharpe_std, confidence_level)
    if lcb_sharpe >= threshold:
        print("Policy passed the HCOPE gate; proceeding with execution.")
        return True
    print(
        f"Policy failed the HCOPE gate. LCB {lcb_sharpe} is below the threshold {threshold}."
    )
    return False
