from validation.purged_kfold import PurgedKFold
from validation.wfo_runner import run_wfo


def test_purged_kfold_embargo_and_purge():
    starts = list(range(10))
    t1 = [s + 1 for s in starts]
    pkf = PurgedKFold(n_splits=3, embargo_pct=0.1)
    for train_idx, test_idx in pkf.split(starts, t1):
        test_start = starts[test_idx[0]]
        test_end = t1[test_idx[-1]]
        for idx in train_idx:
            # Check no overlap with test interval
            assert not (starts[idx] <= test_end and t1[idx] >= test_start)
            # Check simple embargo of 1 observation on each side
            assert idx < test_idx[0] - 1 or idx > test_idx[-1] + 1


def test_run_wfo_returns_metrics():
    data = [
        {"start": float(i), "t1": float(i + 1), "return": (1 if i % 2 == 0 else -1) * 0.01}
        for i in range(12)
    ]
    results = run_wfo(data, n_splits=3, embargo_pct=0.0)
    assert len(results) == 3
    for row in results:
        assert {"fold", "sharpe", "maxdd", "variance"} <= set(row)
        # basic sanity checks
        assert isinstance(row["sharpe"], float)
        assert isinstance(row["maxdd"], float)
        assert isinstance(row["variance"], float)
