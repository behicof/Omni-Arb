"""High-confidence off-policy evaluation utilities.

This module estimates a lower confidence bound on the expected reward of a
new policy using importance sampling and Hoeffding's inequality.  It can be
used as a safety gate before scaling a policy in live trading environments.
"""

from __future__ import annotations

import argparse
import json
from math import log, sqrt
from typing import Sequence, List


def lower_confidence_bound(
    rewards: Sequence[float],
    behavior_probs: Sequence[float],
    target_probs: Sequence[float],
    delta: float = 0.05,
) -> float:
    """Return the lower confidence bound for a new policy.

    Args:
        rewards: Observed rewards from logged interactions.
        behavior_probs: Probabilities of actions taken by the behavior policy.
        target_probs: Probabilities of actions under the new policy.
        delta: Confidence level (default 0.05 for 95% confidence).

    Returns:
        A conservative estimate of the new policy's expected reward.
    """
    if not (len(rewards) == len(behavior_probs) == len(target_probs)):
        raise ValueError("All input sequences must have the same length")
    if not rewards:
        raise ValueError("Input sequences must not be empty")
    if any(b == 0 for b in behavior_probs):
        raise ValueError("behavior_probs contains zero, cannot divide")
    if not (0 < delta < 1):
        raise ValueError("delta must be between 0 and 1")

    weighted_rewards = [r * (t / b) for r, b, t in zip(rewards, behavior_probs, target_probs)]
    estimate = sum(weighted_rewards) / len(weighted_rewards)
    bound = sqrt(log(1 / delta) / (2 * len(weighted_rewards)))
    return estimate - bound


def evaluate_file(path: str, threshold: float, delta: float = 0.05) -> float:
    """Evaluate a JSON log file and enforce a minimum lower bound.

    The JSON file should contain a list of objects with ``reward``,
    ``behavior_prob`` and ``target_prob`` fields.
    """
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    rewards: List[float] = [d["reward"] for d in data]
    behavior = [d["behavior_prob"] for d in data]
    target = [d["target_prob"] for d in data]
    lcb = lower_confidence_bound(rewards, behavior, target, delta)
    print(f"Lower confidence bound: {lcb}")
    if lcb < threshold:
        raise SystemExit(f"LCB {lcb} below threshold {threshold}")
    return lcb


def main() -> None:
    parser = argparse.ArgumentParser(description="High-confidence OPE gate")
    parser.add_argument("--input", required=True, help="Path to JSON trajectory data")
    parser.add_argument("--threshold", type=float, default=0.0,
                        help="Minimum acceptable lower confidence bound")
    parser.add_argument("--delta", type=float, default=0.05,
                        help="Confidence level (1-delta)")
    args = parser.parse_args()
    evaluate_file(args.input, args.threshold, args.delta)


if __name__ == "__main__":
    main()
