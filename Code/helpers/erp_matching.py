"""Timing matching for two sets of trials in the same recording and jump direction."""

import numpy as np
from scipy.optimize import linear_sum_assignment


def match_by_timing(first, second):
    """Maximise pair count and minimise total absolute RT and jump-delay gaps."""
    a = np.array([[r["reaction_ms"], 2 * r["jump_delay_samples"]] for r in first])
    b = np.array([[r["reaction_ms"], 2 * r["jump_delay_samples"]] for r in second])
    gaps = a[:, None, :] - b[None, :, :]
    first_ids, second_ids = linear_sum_assignment(np.abs(gaps).sum(axis=2))
    return ((i, j, gaps[i, j]) for i, j in zip(first_ids, second_ids))
