"""Match manuscript trajectory classes and summarise their jump-aligned EEG."""

from collections import Counter, defaultdict
import argparse
import csv
import gzip
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from helpers.erp_matching import match_by_timing
from helpers.erp_report_encoding import pack_waveforms
from research_paths import result_path


CLASSES = ("error", "correction")


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_rows(path, records):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def prepare(out):
    audit = read_rows(result_path("AUD_02") / "trial_audit.csv.gz")
    labels = {(row["run"], row["trial"]): row["manuscript_label"] for row in audit
              if row["condition"] == "D" and row["eeg_accepted"] == "1"}
    trials = read_rows(result_path("ERP_02") / "trial_selection.csv")
    assert len(labels) == len(trials) and len(labels) == len({(r["run"], r["trial"]) for r in trials})
    groups = defaultdict(list)
    coverage = defaultdict(Counter)
    for trial in trials:
        label = labels[trial["run"], trial["trial"]]
        key = trial["subject"], trial["session"], trial["cohort"]
        coverage[key][label] += 1
        if label in CLASSES:
            for field in ("reaction_ms", "jump_delay_samples"):
                trial[field] = int(trial[field])
            groups[trial["run"], trial["side"]].append((label, trial))

    pairs = []
    for (run, side), group in sorted(groups.items()):
        erroneous, corrective = ([row for label, row in group if label == target] for target in CLASSES)
        if not erroneous or not corrective:
            continue
        for i, j, (reaction_gap, delay_gap) in match_by_timing(corrective, erroneous):
            c, e = corrective[i], erroneous[j]
            key = c["subject"], c["session"], c["cohort"]
            assert key == (e["subject"], e["session"], e["cohort"])
            pairs.append(dict(run=run, side=side, subject=key[0], session=key[1], cohort=key[2],
                              corrective_trial=c["trial"], erroneous_trial=e["trial"],
                              corrective_jump_samples=c["jump_delay_samples"],
                              erroneous_jump_samples=e["jump_delay_samples"],
                              reaction_gap_ms=int(reaction_gap), jump_delay_gap_ms=int(delay_gap)))
            coverage[key]["pairs"] += 1

    used = {(p["run"], p[side]) for p in pairs for side in ("corrective_trial", "erroneous_trial")}
    assert len(used) == 2 * len(pairs)
    out.mkdir(parents=True, exist_ok=True)
    write_rows(out / "matched_pairs.csv", pairs)
    write_rows(out / "coverage.csv", [
        dict(subject=s, session=v, cohort=c, accepted_displaced=sum(n[k] for k in ("correction", "error", "slow", "unknown")),
             corrective=n["correction"], erroneous=n["error"], other_labels=n["slow"] + n["unknown"],
             matched_pairs=n["pairs"]) for (s, v, c), n in sorted(coverage.items())
    ])
    print(f"{len(pairs):,} matched corrective–erroneous pairs")


def means_from_sums(sums, counts):
    return np.divide(sums, counts, out=np.full_like(sums, np.nan), where=counts > 0)


def summarise(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from scipy.io import loadmat

    data = loadmat(out / "tmp/waveform_sums.mat", simplify_cells=True)
    time, channels = data["jumpMs"], list(data["channels"])
    sums, counts = data["waveformSums"], data["pairCounts"]
    subjects, sessions = list(data["subjects"]), list(data["sessions"])
    pairs = read_rows(out / "matched_pairs.csv")
    cohorts = {r["subject"]: r["cohort"] for r in pairs}
    assert counts.sum() == len(pairs)
    windows = json.loads((result_path("ERP_02") / "windows.json").read_text(encoding="utf-8"))
    views = [*zip(sessions, sums.transpose(4, 0, 1, 2, 3), counts.T),
             ("pooled", sums.sum(axis=-1), counts.sum(axis=-1))]

    participant_rows, group_rows = [], []
    for session, wave_sums, n in views:
        averages = means_from_sums(wave_sums, n)
        for window in windows:
            mask = (time >= window["start_ms"]) & (time < window["end_ms_exclusive"])
            indices = [channels.index(e) for e in window["electrodes"]]
            values = averages[mask][:, indices].mean(axis=(0, 1))
            differences = values[1] - values[0]
            meta = dict(component_window=window["component_window"], electrodes="/".join(window["electrodes"]),
                        start_ms=window["start_ms"], end_ms_exclusive=window["end_ms_exclusive"])
            for i, subject in enumerate(subjects):
                if n[i]:
                    participant_rows.append(dict(subject=subject, session=session, cohort=cohorts[subject],
                                                 **meta, matched_pairs=n[i], erroneous_uv=values[0, i],
                                                 corrective_uv=values[1, i], difference_uv=differences[i]))
            for cohort in ("validation", "pilot"):
                use = np.array([cohorts[s] == cohort for s in subjects]) & (n > 0)
                if use.any():
                    diff = differences[use]
                    group_rows.append(dict(cohort=cohort, session=session, **meta, participants=use.sum(),
                                           matched_pairs=n[use].sum(), mean_difference_uv=diff.mean(),
                                           median_difference_uv=np.median(diff),
                                           positive_participants=(diff > 0).sum()))
    write_rows(out / "participant_amplitudes.csv", participant_rows)
    write_rows(out / "group_summary.csv", group_rows)
    for name in ("reaction_gap_ms", "jump_delay_gap_ms"):
        gaps = np.abs([int(row[name]) for row in pairs])
        print(name, "absolute median / p95:", *np.percentile(gaps, [50, 95]))
    for row in group_rows:
        if row["component_window"] == "Interaction negativity":
            print(row)

    pooled = means_from_sums(sums.sum(axis=-1), counts.sum(axis=-1))
    use = np.array([cohorts[s] == "validation" for s in subjects]) & (counts.sum(axis=-1) > 0)
    erroneous, corrective = pooled[..., use].mean(axis=-1).transpose(2, 0, 1)
    fig, axes = plt.subplots(2, 4, figsize=(12.8, 6.2), sharex=True, sharey=True)
    for ch, ax in enumerate(axes.flat):
        ax.axvline(0, color="#53657a", lw=.8, ls=":")
        ax.axhline(0, color=".75", lw=.6)
        for trace, color in zip((erroneous, corrective, corrective - erroneous),
                                ("#53657a", "#137f6a", "#27232b")):
            ax.plot(time, trace[:, ch], color=color, lw=1.35)
        ax.set(title=channels[ch], xlim=(-500, 500))
        ax.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Corrective versus erroneous displaced reaches · aligned to target jump")
    fig.supxlabel("Time from jump (ms)")
    fig.supylabel("Amplitude (µV)")
    fig.legend(axes.flat[-1].lines[-3:], ("Erroneous", "Corrective", "Corrective minus erroneous"),
               loc="lower center", bbox_to_anchor=(.5, .04), ncol=3, frameon=False)
    fig.tight_layout(rect=(.01, .08, 1, .96))
    fig.savefig(out / "jump_corrective_vs_erroneous.png", dpi=150)
    plt.close(fig)

    descriptor = pack_waveforms(time, sums[:, :, :, None, :, :], counts[None, :, :])
    descriptor["subsets"] = 1
    payload = dict(subjects=subjects, sessions=sessions, channels=channels, cohorts=cohorts,
                   counts=counts[:, :, None].tolist(), waveforms={"jump": descriptor})
    (out / "waveform_means.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("prepare", "summarise"))
    args = parser.parse_args()
    (prepare if args.step == "prepare" else summarise)(result_path("ERP_03"))
