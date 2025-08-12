from ope.hcope import lower_confidence_bound, evaluate_file


def test_lower_confidence_bound():
    rewards = [1.0, 0.0, 1.0, 1.0]
    behavior = [0.5, 0.5, 0.5, 0.5]
    target = [0.6, 0.4, 0.7, 0.5]
    lcb = lower_confidence_bound(rewards, behavior, target)
    assert 0.0 < lcb < 1.0


def test_evaluate_file_threshold_passes():
    path = "tests/sample_trajectory.json"
    lcb = evaluate_file(path, threshold=0.1)
    assert lcb > 0.1
