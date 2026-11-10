"""Test pooled 40 px D-hit minus matched ND-hit waveforms from ERP_04."""

from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import loadmat
from scipy.stats import t, ttest_1samp

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from research_paths import result_path
from compare_observed_outcomes import read_rows, write_rows


REGIONS = {"Cz/FCz": ("Cz", "FCz"), "P3/PO3/PO7": ("P3", "PO3", "PO7")}
N_RANDOM = 19999
SEED = 2026
SEARCH_MS = (0, 500)
N100_MS = (80, 150)


def clusters(t_values, threshold):
    """Yield same-sign runs of suprathreshold samples within each region."""
    for region, curve in enumerate(t_values):
        for sign in (1, -1):
            signed = sign * curve
            boundaries = np.flatnonzero(np.diff(signed > threshold, prepend=False, append=False))
            for start, stop in zip(boundaries[::2], boundaries[1::2]):
                yield region, sign, start, stop, signed[start:stop].sum()


def cluster_test(differences, time, n_pairs):
    """Use one sign per participant, jointly for all tested times and regions."""
    n, n_regions, n_times = differences.shape
    flat = differences.reshape(n, -1)
    threshold = t.ppf(.975, n - 1)
    sum_squares = np.square(flat).sum(axis=0)

    def t_values(sums):
        denominator = np.sqrt(np.maximum(0, n * sum_squares - sums**2))
        return np.divide(sums * np.sqrt(n - 1), denominator, out=np.zeros_like(sums), where=denominator > 0)

    observed = t_values(flat.sum(axis=0)).reshape(n_regions, n_times)
    assert np.allclose(observed, ttest_1samp(differences, 0, axis=0).statistic)
    rng = np.random.default_rng(SEED)
    null = []
    for first in range(0, N_RANDOM, 512):
        size = min(512, N_RANDOM - first)
        signs = 2 * rng.integers(0, 2, size=(size, n), dtype=np.int8) - 1
        random_t = t_values(signs @ flat).reshape(size, n_regions, n_times)
        for trial in random_t:
            null.append(max((c[-1] for c in clusters(trial, threshold)), default=0))
    null = np.array(null)

    records = []
    for region, sign, start, stop, mass in clusters(observed, threshold):
        result = differences[:, region, start:stop].mean(axis=1)
        records.append(dict(
            electrodes=list(REGIONS)[region], polarity="positive" if sign == 1 else "negative",
            start_ms=int(time[start]), end_ms_exclusive=int(time[stop - 1] + 2),
            participants=n, matched_pairs=n_pairs, mean_difference_uv=result.mean(),
            cluster_mass=mass, p_cluster=(1 + np.count_nonzero(null >= mass)) / (1 + N_RANDOM),
        ))
    return sorted(records, key=lambda row: (row["p_cluster"], row["electrodes"], row["start_ms"]))


def group_summary(sums, counts):
    use = counts > 0
    return sums[..., use] / counts[use], int(counts[use].sum())


def main():
    out = result_path("ERP_04")
    data = loadmat(out / "tmp/waveform_sums.mat", simplify_cells=True)
    contrast = list(data["contrasts"]).index("d_nd_hit")
    time = data["jumpMs"]
    keep = (time >= SEARCH_MS[0]) & (time < SEARCH_MS[1])
    time = time[keep]
    assert np.array_equal(time, np.arange(*SEARCH_MS, 2))
    channels = list(data["channels"])
    cohorts = {r["subject"]: r["cohort"] for r in read_rows(out / "matched_pairs.csv")}
    nonpilot = np.array([cohorts[s] == "validation" for s in data["subjects"]])
    sums = data["waveformSums"][keep, :, :, contrast]
    difference = sums[:, :, 1] - sums[:, :, 0]
    roi_sums = np.stack([difference[:, [channels.index(ch) for ch in group]].mean(axis=1)
                         for group in REGIONS.values()])
    counts = data["pairCounts"][contrast, nonpilot, :]
    roi_sums = roi_sums[:, :, nonpilot]
    pooled, n_pairs = group_summary(roi_sums.sum(axis=-1), counts.sum(axis=-1))
    participant_data = pooled.transpose(2, 0, 1)
    assert participant_data.shape[1:] == (len(REGIONS), len(time))
    assert np.isfinite(participant_data).all()

    results = cluster_test(participant_data, time, n_pairs)
    if results:
        write_rows(out / "matched_hit_clusters.csv", results)
    else:
        (out / "matched_hit_clusters.csv").write_text(
            "electrodes,polarity,start_ms,end_ms_exclusive,participants,matched_pairs,mean_difference_uv,cluster_mass,p_cluster\n",
            encoding="utf-8",
        )
    supported = [row for row in results if row["p_cluster"] < .05]

    early = (time >= N100_MS[0]) & (time < N100_MS[1])
    posterior = list(REGIONS).index("P3/PO3/PO7")
    n100 = participant_data[:, posterior, early].mean(axis=1)
    test = ttest_1samp(n100, 0)
    ci = test.confidence_interval()
    n100_row = dict(electrodes=list(REGIONS)[posterior], start_ms=N100_MS[0], end_ms_exclusive=N100_MS[1],
                    participants=len(n100), matched_pairs=n_pairs, mean_difference_uv=n100.mean(),
                    ci95_low_uV=ci.low, ci95_high_uV=ci.high, p=test.pvalue)
    write_rows(out / "matched_hit_n100.csv", [n100_row])

    sessions = {session: group_summary(roi_sums[..., i], counts[:, i])
                for i, session in enumerate(data["sessions"])}
    session_rows = []
    for row in supported:
        region = list(REGIONS).index(row["electrodes"])
        mask = (time >= row["start_ms"]) & (time < row["end_ms_exclusive"])
        for session, (values, pairs) in sessions.items():
            mean = values[region, mask].mean(axis=0)
            session_rows.append(dict(electrodes=row["electrodes"], start_ms=row["start_ms"],
                                     end_ms_exclusive=row["end_ms_exclusive"], session=session,
                                     participants=len(mean), matched_pairs=pairs,
                                     mean_difference_uv=mean.mean(), positive_participants=int((mean > 0).sum())))
    if session_rows:
        write_rows(out / "matched_hit_cluster_sessions.csv", session_rows)
    else:
        (out / "matched_hit_cluster_sessions.csv").write_text(
            "electrodes,start_ms,end_ms_exclusive,session,participants,matched_pairs,mean_difference_uv,positive_participants\n",
            encoding="utf-8",
        )

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4), sharex=True, sharey=True)
    for i, region in enumerate(REGIONS):
        for ax in axes[:, i]:
            ax.axhline(0, color=".7", lw=.8)
            for row in supported:
                if row["electrodes"] == region:
                    ax.axvspan(row["start_ms"], row["end_ms_exclusive"], color="#d8eaf7", lw=0)
            ax.set_xlim(*SEARCH_MS)
            ax.spines[["top", "right"]].set_visible(False)
        top, bottom = axes[:, i]
        top.set_title("Pooled · " + region)
        bottom.set_title("By session · " + region)
        top.plot(time, pooled[i].mean(axis=1), color="#20334b", lw=1.6)
        for (session, (values, _)), color in zip(sessions.items(), ("#1864a4", "#a35125", "#087f67")):
            bottom.plot(time, values[i].mean(axis=1), color=color, lw=1.4, label=session.capitalize())
    fig.suptitle("Matched D hits minus ND hits · 40 px")
    fig.supylabel("Mean difference (µV)")
    fig.supxlabel("Time from jump / pseudo-jump (ms)")
    fig.legend(*axes[1, 0].get_legend_handles_labels(), ncol=3, frameon=False,
               loc="lower center", bbox_to_anchor=(.5, .04))
    fig.tight_layout(rect=(.025, .09, 1, .95))
    fig.savefig(out / "matched_hit_clusters.png", dpi=155)
    plt.close(fig)

    for row in supported:
        print(row)
    print("N100", n100_row)
    for row in session_rows:
        print(row)


if __name__ == "__main__":
    main()
