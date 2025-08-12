"""High-confidence off-policy evaluation (HCOPE).

Provides a simple utility to compute a lower confidence bound (LCB)
for the expected return of a target policy using importance sampling
rewards. This estimate can be used to decide whether a new policy is
safe to deploy before scaling LIVE traffic.
"""
from __future__ import annotations

from typing import Sequence
from statistics import NormalDist, mean, variance
from math import sqrt


def lower_confidence_bound(
    rewards: Sequence[float],
    weights: Sequence[float] | None = None,
    delta: float = 0.05,
) -> float:
    r"""Estimate a lower confidence bound on the policy value.

    Parameters
    ----------
    rewards:
        Observed rewards from the behaviour policy.
    weights:
        Importance weights for each reward. If ``None``, equal weights
        are assumed which reduces to the on-policy case.
    delta:
        Confidence level :math:`1-\delta`. ``delta=0.05`` corresponds to a
        95\% one-sided confidence interval.

    Returns
    -------
    float
        Lower confidence bound of the target policy's expected return.

    Notes
    -----
    We use a normal approximation to compute the bound. For ``n`` samples
    with weighted rewards :math:`x_i`, the estimate is

    .. math::

        \bar{x} - z_{1-\delta}\frac{\sigma}{\sqrt{n}}

    where :math:`z_{1-\delta}` is the normal quantile and :math:`\sigma`
    is the sample standard deviation of ``x_i``. This provides a
    lightweight, distribution-free lower bound suitable for gating new
    policies before LIVE scaling.
    """
    if not rewards:
        raise ValueError("rewards must not be empty")

    n = len(rewards)
    if weights is None:
        weights = [1.0] * n
    if len(weights) != n:
        raise ValueError("rewards and weights must have the same length")

    weighted = [r * w for r, w in zip(rewards, weights)]
    mu = mean(weighted)
    if n == 1:
        # With a single sample we cannot estimate variability; return the mean.
        return mu

    # Sample standard deviation. ``variance`` uses n-1 in denominator by default.
    sigma = sqrt(variance(weighted))
    stderr = sigma / sqrt(n)

    z = NormalDist().inv_cdf(1 - delta)
    return mu - z * stderr

__all__ = ["lower_confidence_bound"]
