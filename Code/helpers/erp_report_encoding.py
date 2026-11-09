"""Pack ERP means for offline browser plots."""

import base64
import gzip

import numpy as np


def pack_waveforms(time, sums, counts):
    """Encode time × channel × class × subset × participant × session means."""
    denominator = counts[None, None, None, :, :, :]
    means = np.divide(sums, denominator, out=np.zeros_like(sums), where=denominator > 0)
    assert np.max(np.abs(means)) <= 100.000001
    # Hundredths of a microvolt fit in signed 16 bits. Preserve the 500 Hz grid.
    packed = np.rint(means.transpose(4, 5, 3, 2, 1, 0) * 100).astype("<i2")
    deltas = np.diff(packed, axis=-1, prepend=np.zeros_like(packed[..., :1]))
    return dict(
        first_ms=int(time[0]), step_ms=2, samples=packed.shape[-1],
        gzip=base64.b64encode(gzip.compress(deltas.tobytes(), mtime=0)).decode("ascii"),
    )
