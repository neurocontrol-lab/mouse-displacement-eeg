"""Shared adjustment for ERP window tests."""

import numpy as np


def holm(p_values):
    p_values = np.asarray(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty_like(p_values)
    adjusted[order] = np.minimum(1, np.maximum.accumulate(
        p_values[order] * np.arange(len(order), 0, -1)
    ))
    return adjusted
