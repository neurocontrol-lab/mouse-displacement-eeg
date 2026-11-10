"""Match observed outcome groups and describe their jump-aligned EEG."""

import argparse
from collections import Counter, defaultdict
import csv
import gzip
import json
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.stats import ttest_1samp

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from helpers.erp_matching import match_by_timing
from helpers.erp_report_encoding import pack_waveforms
from helpers.erp_stats import holm
from research_paths import result_path


CONTRASTS = {
    "hit": ("D no hit detected", "D hit detected", "Observed hit in displaced trials"),
    "hit400": ("D no hit by 400 ms", "D hit by 400 ms", "Observed hit by 400 ms"),
    "near75": ("D no approach within 75 px", "D reached within 75 px", "Close approach at 75 px"),
    "near100": ("D no approach within 100 px", "D reached within 100 px", "Close approach at 100 px"),
    "d_nd_hit": ("ND hit detected", "D hit detected", "Displaced versus non-displaced hits"),
}


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_rows(path, records):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def load_trials():
    outcomes = result_path("AUD_02") / "target_boundary/observed_hit_trials.csv.gz"
    labels = {(r["run"], r["trial"]): r for r in read_rows(outcomes)}
    timing = {(r["run"], r["trial"]): r for r in read_rows(result_path("AUD_01") / "observed_onsets.csv.gz")}
    sides = {(r["run"], r["trial"]): int(r["jump_direction"])
             for r in read_rows(result_path("AUD_02") / "trial_audit.csv.gz")}
    metadata = read_rows(result_path("DEC_02") / "trial_metadata.csv")
    assert len(labels) == len(metadata) == len({(r["run"], r["trial"]) for r in metadata})
    trials = []
    for row in metadata:
        key = row["run"], row["trial"]
        label, time = labels[key], timing[key]
        assert row["label"] == time["label"]
        assert (row["label"] == "2") == (label["condition"] == "D")
        jump = int(time["jump_eeg_sample"]) - int(time["movement_eeg_sample"]) if row["label"] == "2" else None
        if jump is not None:
            assert 0 < jump <= 250
        first = float(label["first_hit_ms_from_anchor"]) if label["first_hit_ms_from_anchor"] else None
        assert (first is not None) == (label["outcome"] == "hit_detected")
        trials.append(dict(
            **row, side=sides[key],
            reaction_ms=int(time["movement_eeg_ms_from_target"]), jump_delay_samples=jump,
            first_hit_ms=first, observed_ms=float(label["observed_through_ms_from_anchor"]),
            near75=label["close_75"] == "1", near100=label["close_100"] == "1",
        ))
    return sorted(trials, key=lambda r: (r["run"], int(r["trial"])))


def eligible_group(row, contrast):
    hit = row["first_hit_ms"]
    if contrast == "d_nd_hit":
        return int(row["label"] == "2") if hit is not None else None
    if row["label"] != "2":
        return None
    if contrast == "hit400":
        return int(hit is not None and hit <= 400) if row["observed_ms"] >= 400 else None
    if contrast == "hit":
        return int(hit is not None)
    return int(row[contrast])


def match_hit_controls(first, second):
    """Match D to ND on reaction time, requiring ND entry after the pseudo-jump."""
    delays = 2 * np.array([r["jump_delay_samples"] for r in first])
    nd_entries = np.array([r["first_hit_ms"] for r in second])
    gaps = np.array([r["reaction_ms"] for r in first])[:, None] - np.array([r["reaction_ms"] for r in second])
    compatible = nd_entries[None, :] >= delays[:, None]
    cost = np.abs(gaps)
    penalty = (1 + cost.max()) * (1 + min(cost.shape))
    first_ids, second_ids = linear_sum_assignment(np.where(compatible, cost, penalty))
    return ((i, j, (gaps[i, j], None)) for i, j in zip(first_ids, second_ids) if compatible[i, j])


def prepare(out):
    pairs, coverage = [], []
    trials = load_trials()
    for contrast in CONTRASTS:
        groups = defaultdict(lambda: ([], []))
        counts = defaultdict(Counter)
        for row in trials:
            group = eligible_group(row, contrast)
            if group is None:
                continue
            stratum = (row["run"], 0 if contrast == "d_nd_hit" else row["side"])
            groups[stratum][group].append(row)
            counts[row["subject"], row["session"], row["cohort"]][group] += 1
        used = set()
        for (run, _), (reference, comparison) in sorted(groups.items()):
            if not reference or not comparison:
                continue
            matcher = match_hit_controls if contrast == "d_nd_hit" else match_by_timing
            for i, j, (rt_gap, delay_gap) in matcher(comparison, reference):
                c, r = comparison[i], reference[j]
                key = c["subject"], c["session"], c["cohort"]
                assert key == (r["subject"], r["session"], r["cohort"])
                assert (run, c["trial"]) not in used and (run, r["trial"]) not in used
                used.update(((run, c["trial"]), (run, r["trial"])))
                pairs.append(dict(
                    contrast=contrast, run=run, subject=key[0], session=key[1], cohort=key[2],
                    jump_side=c["side"], reference_trial=r["trial"], comparison_trial=c["trial"],
                    reference_label=r["label"], comparison_label=c["label"],
                    reference_jump_samples=r["jump_delay_samples"] or c["jump_delay_samples"],
                    comparison_jump_samples=c["jump_delay_samples"], reaction_gap_ms=rt_gap,
                    jump_delay_gap_ms=delay_gap,
                ))
                counts[key]["pairs"] += 1
        coverage.extend(dict(contrast=contrast, subject=s, session=v, cohort=c,
                             reference_trials=n[0], comparison_trials=n[1], matched_pairs=n["pairs"])
                        for (s, v, c), n in sorted(counts.items()))
    out.mkdir(parents=True, exist_ok=True)
    write_rows(out / "matched_pairs.csv", pairs)
    write_rows(out / "coverage.csv", coverage)
    print(dict(Counter(r["contrast"] for r in pairs)))


def plot_cohort(out, contrast, time, channels, averages):
    import matplotlib.pyplot as plt

    reference, comparison, title = CONTRASTS[contrast]
    a, b = averages.transpose(2, 0, 1)
    fig, axes = plt.subplots(2, 4, figsize=(12.8, 6.2), sharex=True, sharey=True)
    for i, ax in enumerate(axes.flat):
        ax.axvline(0, color="#53657a", lw=.8, ls=":")
        ax.axhline(0, color=".75", lw=.6)
        handles = []
        for trace, color in zip((a, b, b - a), ("#53657a", "#137f6a", "#27232b")):
            handles += ax.plot(time, trace[:, i], color=color, lw=1.35)
        ax.set(title=channels[i], xlim=(-500, 500))
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle(title + " · non-pilot cohort")
    fig.supxlabel("Time from jump / pseudo-jump (ms)" if contrast == "d_nd_hit" else "Time from jump (ms)")
    fig.supylabel("Amplitude (µV)")
    fig.legend(handles, (reference, comparison, "Difference"), loc="lower center",
               bbox_to_anchor=(.5, .04), ncol=3, frameon=False)
    fig.tight_layout(rect=(.01, .08, 1, .96))
    fig.savefig(out / f"outcome_{contrast}.png", dpi=150)
    plt.close(fig)


def save_hit_inference(out, participant_rows):
    """Test the five existing windows on pooled, matched D and ND hits."""
    windows = defaultdict(list)
    fields = ("component_window", "electrodes", "start_ms", "end_ms_exclusive")
    for row in participant_rows:
        if row["cohort"] == "validation" and row["session"] == "pooled" and row["contrast"] == "d_nd_hit":
            windows[tuple(row[k] for k in fields)].append(row)

    tests = []
    for window, rows in windows.items():
        values = np.array([r["difference_uv"] for r in rows])
        test = ttest_1samp(values, 0)
        interval = test.confidence_interval()
        tests.append(dict(alignment="jump", **dict(zip(fields, window)),
                          participants=len(values), matched_pairs=sum(r["matched_pairs"] for r in rows),
                          mean_D_minus_ND_uV=values.mean(), ci95_low_uV=interval.low,
                          ci95_high_uV=interval.high, p=test.pvalue))
    for row, adjusted in zip(tests, holm([row["p"] for row in tests])):
        row["p_Holm"] = adjusted
    write_rows(out / "matched_hit_window_tests.csv", tests)


def summarise(out):
    import matplotlib
    matplotlib.use("Agg")
    from scipy.io import loadmat

    data = loadmat(out / "tmp/waveform_sums.mat", simplify_cells=True)
    time, channels = data["jumpMs"], list(data["channels"])
    subjects, sessions = list(data["subjects"]), list(data["sessions"])
    pairs = read_rows(out / "matched_pairs.csv")
    cohorts = {r["subject"]: r["cohort"] for r in pairs}
    windows = json.loads((result_path("ERP_02") / "windows.json").read_text(encoding="utf-8"))
    participant_rows, group_rows, descriptors = [], [], {}
    for i, contrast in enumerate(data["contrasts"]):
        sums, counts = data["waveformSums"][:, :, :, i], data["pairCounts"][i]
        selected_pairs = [r for r in pairs if r["contrast"] == contrast]
        assert counts.sum() == len(selected_pairs)
        reference, comparison, _ = CONTRASTS[contrast]
        desc = pack_waveforms(time, sums[:, :, :, None, :, :], counts[None, :, :])
        desc.update(subsets=1, counts=counts[:, :, None].tolist())
        descriptors["outcome_" + contrast] = desc
        for visit, wave_sums, n in [*zip(sessions, sums.transpose(4, 0, 1, 2, 3), counts.T),
                                    ("pooled", sums.sum(axis=-1), counts.sum(axis=-1))]:
            means = np.divide(wave_sums, n, out=np.full_like(wave_sums, np.nan), where=n > 0)
            for window in windows:
                mask = (time >= window["start_ms"]) & (time < window["end_ms_exclusive"])
                indices = [channels.index(e) for e in window["electrodes"]]
                values = means[mask][:, indices].mean(axis=(0, 1))
                diff = values[1] - values[0]
                meta = dict(contrast=contrast, session=visit, reference=reference, comparison=comparison,
                            component_window=window["component_window"], electrodes="/".join(window["electrodes"]),
                            start_ms=window["start_ms"], end_ms_exclusive=window["end_ms_exclusive"])
                for p, subject in enumerate(subjects):
                    if n[p]:
                        participant_rows.append(dict(subject=subject, cohort=cohorts[subject], **meta,
                                                     matched_pairs=n[p], reference_uv=values[0,p],
                                                     comparison_uv=values[1,p], difference_uv=diff[p]))
                for cohort in ("validation", "pilot"):
                    use = np.array([cohorts[s] == cohort for s in subjects]) & (n > 0)
                    if use.any():
                        group_rows.append(dict(cohort=cohort, **meta, participants=use.sum(),
                                               matched_pairs=n[use].sum(), mean_difference_uv=diff[use].mean(),
                                               median_difference_uv=np.median(diff[use]),
                                               positive_participants=(diff[use] > 0).sum()))
            if visit == "pooled":
                use = np.array([cohorts[s] == "validation" for s in subjects]) & (n > 0)
                plot_cohort(out, contrast, time, channels, means[..., use].mean(axis=-1))
        print(contrast, "pairs", len(selected_pairs), "median absolute RT gap",
              np.median([abs(int(r["reaction_gap_ms"])) for r in selected_pairs]))
    write_rows(out / "participant_amplitudes.csv", participant_rows)
    write_rows(out / "group_summary.csv", group_rows)
    save_hit_inference(out, participant_rows)
    payload = dict(subjects=subjects, sessions=sessions, channels=channels, cohorts=cohorts,
                   waveforms=descriptors, labels={"outcome_" + k: v[:2] for k, v in CONTRASTS.items()})
    (out / "waveform_means.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("prepare", "summarise"))
    args = parser.parse_args()
    (prepare if args.step == "prepare" else summarise)(result_path("ERP_04"))
