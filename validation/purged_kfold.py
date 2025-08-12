"""Purged K-Fold cross-validator with optional embargo."""

from __future__ import annotations

from typing import Iterator, List, Sequence, Tuple


class PurgedKFold:
    """K-fold cross-validation respecting label overlap.

    Parameters
    ----------
    n_splits : int
        Number of folds. Must be at least 2.
    embargo_pct : float, optional
        Fraction of the dataset to embargo on each side of the test fold.
    """

    def __init__(self, n_splits: int = 5, embargo_pct: float = 0.0) -> None:
        if n_splits < 2:
            raise ValueError("n_splits must be at least 2")
        if not 0.0 <= embargo_pct < 0.5:
            raise ValueError("embargo_pct must be in [0, 0.5)")
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct

    def split(
        self, starts: Sequence[float], t1: Sequence[float]
    ) -> Iterator[Tuple[List[int], List[int]]]:
        """Generate indices to split data into training and test set.

        The ``starts`` sequence represents the beginning timestamp of each
        observation and ``t1`` the corresponding ending timestamp. Both
        sequences must be sorted by ``starts`` in ascending order.
        """

        n_samples = len(starts)
        if n_samples != len(t1):
            raise ValueError("starts and t1 must be the same length")
        indices = list(range(n_samples))

        # Determine test folds using a simple array split.
        fold_sizes = [n_samples // self.n_splits] * self.n_splits
        for i in range(n_samples % self.n_splits):
            fold_sizes[i] += 1
        test_folds: List[List[int]] = []
        current = 0
        for fold_size in fold_sizes:
            test_folds.append(indices[current : current + fold_size])
            current += fold_size

        embargo = int(self.embargo_pct * n_samples)

        for test_indices in test_folds:
            test_start_idx = test_indices[0]
            test_end_idx = test_indices[-1]
            test_start = starts[test_start_idx]
            test_end = t1[test_end_idx]

            train_indices: List[int] = []
            for idx in indices:
                if idx in test_indices:
                    continue
                if embargo and (test_start_idx - embargo <= idx <= test_end_idx + embargo):
                    continue
                start_i = starts[idx]
                end_i = t1[idx]
                if start_i <= test_end and end_i >= test_start:
            # Compute embargo window after the test set
            if embargo > 0.0:
                # Embargo window is a fraction of the total time range
        for test_indices in test_folds:
            test_start_idx = test_indices[0]
            test_end_idx = test_indices[-1]
            test_start = starts[test_start_idx]
            test_end = t1[test_end_idx]

            # Compute embargo window after the test set
            if self.embargo_pct > 0.0:
                total_time = starts[-1] - starts[0]
                embargo_delta = self.embargo_pct * total_time
                embargo_start = test_end
                embargo_end = test_end + embargo_delta
            else:
                embargo_start = embargo_end = None

            train_indices: List[int] = []
            for idx in indices:
                if idx in test_indices:
                    continue
                start_i = starts[idx]
                end_i = t1[idx]
                # Purge observations whose label intervals overlap test set
                if start_i <= test_end and end_i >= test_start:
                    continue
                # Purge observations whose label intervals overlap embargo window
                if embargo_start is not None and embargo_end is not None and start_i <= embargo_end and end_i >= embargo_start:
                    continue
                train_indices.append(idx)

            yield train_indices, test_indices
