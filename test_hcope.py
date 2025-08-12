import math
from ope.hcope import lower_confidence_bound


def test_lcb_is_below_mean():
    rewards = [1, 0, 1, 1, 0]
    weights = [1, 1, 1, 1, 1]
    mean_reward = sum(r * w for r, w in zip(rewards, weights)) / len(rewards)
    lcb = lower_confidence_bound(rewards, weights, delta=0.05)
    assert lcb <= mean_reward
    # For this dataset variance>0, so lcb should be strictly less
    assert lcb < mean_reward


def test_lcb_with_single_sample_returns_mean():
    assert lower_confidence_bound([0.5], [1.0], delta=0.05) == 0.5
