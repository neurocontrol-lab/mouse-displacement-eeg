"""Plot matched ERPs and summarize fixed-window effects across and within participants."""

from collections import Counter, defaultdict
import base64
import csv
import gzip
import json
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


# Half-open windows in ms. Fix these before inspecting the cohort waveforms.
# Sign is a morphology prediction; all tests are two-sided.
WINDOWS = json.loads(Path(__file__).with_name("windows.json").read_text(encoding="utf-8"))
ALIGNMENTS = {"movement": "Movement onset", "jump": "Jump / pseudo-jump"}
CLASS_NAMES = ["Non-displaced", "Displaced", "Displaced minus non-displaced"]
CLASS_COLORS = ["#1f5a96", "#aa4834", "#27232b"]


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def mean_by_participant(sums, counts):
    """Pool sessions within each participant, weighted by available pairs."""
    return sums.sum(axis=-1) / counts.sum(axis=-1)[None, None, None, :, :]


def holm(p_values):
    p_values = np.asarray(p_values)
    order = np.argsort(p_values)
    adjusted = np.empty_like(p_values)
    adjusted[order] = np.minimum(1, np.maximum.accumulate(
        p_values[order] * np.arange(len(order), 0, -1)
    ))
    return adjusted


def panel(ax, time, title):
    ax.axvline(0, color="0.5", lw=.8, ls=":")
    ax.axhline(0, color="0.75", lw=.6)
    ax.set(xlim=(time[0], time[-1] + 2), title=title)
    ax.spines[["top", "right"]].set_visible(False)


def save_figure(fig, path, legend_handles, names):
    fig.supxlabel("Time relative to alignment event (ms)")
    fig.supylabel("Amplitude (µV)")
    fig.legend(legend_handles, names, loc="lower center", bbox_to_anchor=(.5, .04),
               ncol=len(names), frameon=False)
    fig.tight_layout(rect=(.015, .08, 1, .96))
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_waveforms(out, times, sums, counts, channels, sessions, validation, delay_medians):
    pooled = {key: mean_by_participant(data, counts)[..., validation].mean(axis=-1)
              for key, data in sums.items()}
    n = validation.sum()
    fig, axes = plt.subplots(4, 4, figsize=(14, 11), sharex="col")
    fig.suptitle(f"Matched D and ND waveforms · {n} non-pilot participants")
    for c, channel in enumerate(channels):
        row, col = divmod(c, 2)
        limits = []
        for a, (key, alignment) in enumerate(ALIGNMENTS.items()):
            ax = axes[row, col * 2 + a]
            traces = pooled[key][:, c, :, 0]
            curves = np.column_stack((traces, traces[:, 1] - traces[:, 0]))
            handles = ax.plot(times[key], curves, lw=1.4)
            for handle, color in zip(handles, CLASS_COLORS):
                handle.set_color(color)
            limits.append(np.max(np.abs(curves)))
            panel(ax, times[key], f"{channel} · {alignment}")
        for a in range(2):
            axes[row, col * 2 + a].set_ylim(-1.12 * max(limits), 1.12 * max(limits))
    save_figure(fig, out / "matched_waveforms.png", handles, CLASS_NAMES)

    for key, alignment in ALIGNMENTS.items():
        fig, axes = plt.subplots(2, 4, figsize=(13, 6.5), sharex=True, sharey=True)
        fig.suptitle(f"Matched displaced minus non-displaced by session · {alignment}")
        sizes = []
        for c, channel in enumerate(channels):
            ax = axes.flat[c]
            handles = []
            for s, session in enumerate(sessions):
                selected = validation & (counts[0, :, s] > 0)
                traces = sums[key][:, c, :, 0, :, s][..., selected]
                difference = traces[:, 1] - traces[:, 0]
                waveform = (difference / counts[0, selected, s]).mean(axis=1)
                handles.extend(ax.plot(times[key], waveform, lw=1.45))
                if c == 0:
                    sizes.append(f"{session} ({selected.sum()})")
            panel(ax, times[key], channel)
        save_figure(fig, out / f"{key}_differences_by_session.png", handles, sizes)

    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4), sharex="col", sharey="row")
    fig.suptitle("Short vs long recorded jump delays · matched D minus ND")
    for row, (title, electrodes) in enumerate((
        ("Cz / FCz", ["Cz", "FCz"]), ("CP1", ["CP1"]),
    )):
        idx = [channels.index(c) for c in electrodes]
        for col, (key, alignment) in enumerate(ALIGNMENTS.items()):
            ax = axes[row, col]
            traces = pooled[key][:, idx, :, 1:].mean(axis=1)
            handles = ax.plot(times[key], traces[:, 1] - traces[:, 0], lw=1.55)
            panel(ax, times[key], f"{title} · {alignment}")
    save_figure(fig, out / "short_vs_long_delay.png", handles, [
        f"Short (median {delay_medians['short']:.0f} ms)",
        f"Long (median {delay_medians['long']:.0f} ms)",
    ])


def save_report_means(out, subjects, sessions, channels, cohorts, times, sums, counts):
    """Save display means in participant/session/subset/class/channel/sample order."""
    waveforms = {}
    for alignment, values in sums.items():
        denominator = counts[None, None, None, :, :, :]
        means = np.divide(values, denominator, out=np.zeros_like(values),
                          where=denominator > 0)
        assert np.max(np.abs(means)) <= 100.000001
        # Hundredths of a microvolt fit in signed 16 bits. Preserve the 500 Hz grid.
        packed = np.rint(means.transpose(4, 5, 3, 2, 1, 0) * 100).astype("<i2")
        # Differences between successive samples compress well and preserve every packed value.
        deltas = np.diff(packed, axis=-1, prepend=np.zeros_like(packed[..., :1]))
        waveforms[alignment] = dict(
            first_ms=int(times[alignment][0]), step_ms=2, samples=packed.shape[-1],
            gzip=base64.b64encode(gzip.compress(deltas.tobytes(), mtime=0)).decode("ascii"),
        )
    data = dict(subjects=list(subjects), sessions=list(sessions), channels=list(channels),
                cohorts=cohorts, counts=counts.transpose(1, 2, 0).astype(int).tolist(),
                waveforms=waveforms)
    (out / "waveform_means.json").write_text(json.dumps(data, separators=(",", ":")),
                                             encoding="utf-8")


def summarize_run_effects(pairs, data):
    """Resample runs within session and keep the original session pair weights."""
    run_counts = Counter(pair["run"] for pair in pairs)
    run_meta = {pair["run"]: pair for pair in pairs}
    if "runNames" not in data:
        raise ValueError("Rerun extract_matched_waveforms in MATLAB to export recording-level effects.")
    run_names = data["runNames"]
    effects = data["runDeltas"]
    assert len(set(run_names)) == len(run_names) == len(run_counts)
    assert effects.shape == (len(run_names), len(WINDOWS)) and np.isfinite(effects).all()

    by_subject = defaultdict(lambda: defaultdict(list))
    run_rows = []
    for run, values in zip(run_names, effects):
        meta = {key: run_meta[run][key] for key in ("subject", "session", "cohort", "run")}
        count = run_counts[run]
        by_subject[meta["subject"]][meta["session"]].append((count, values))
        for window, value in zip(WINDOWS, values):
            run_rows.append(dict(window_metadata(window), **meta, matched_pairs=count,
                                 D_minus_ND_uV=value))

    rng = np.random.default_rng(10401)
    draws = 20_000
    summary = {}
    for subject, sessions in sorted(by_subject.items()):
        bootstrap = np.zeros((draws, len(WINDOWS)))
        total_pairs = 0
        session_means = {}
        for session, runs in sessions.items():
            counts = np.array([count for count, _ in runs])
            values = np.stack([value for _, value in runs])
            selected = rng.integers(0, len(runs), size=(draws, len(runs)))
            weighted_values = values * counts[:, None]
            resampled_pairs = counts[selected].sum(axis=1, keepdims=True)
            resampled_means = weighted_values[selected].sum(axis=1) / resampled_pairs
            session_pairs = counts.sum()
            bootstrap += session_pairs * resampled_means
            total_pairs += session_pairs
            session_means[session] = weighted_values.sum(axis=0) / session_pairs
        summary[subject] = (
            np.percentile(bootstrap / total_pairs, [2.5, 97.5], axis=0),
            {session: len(runs) for session, runs in sessions.items()},
            session_means,
        )
    return run_rows, summary


def window_metadata(window):
    return dict(window, electrodes="/".join(window["electrodes"]))


def main():
    out = result_path("ERP_01")
    data = loadmat(out / "tmp" / "waveform_sums.mat", simplify_cells=True)
    subjects, sessions, channels = map(data.get, ("subjects", "sessions", "channels"))
    channels = list(channels)
    counts = data["counts"]
    assert np.all(counts.sum(axis=-1) > 0)
    sums = {"movement": data["moveSum"], "jump": data["jumpSum"]}
    times = {"movement": data["moveMs"], "jump": data["jumpMs"]}
    accepted = read_csv(result_path("DEC_02") / "trial_metadata.csv")
    pairs = read_csv(out / "matched_trials.csv")
    run_rows, repeatability = summarize_run_effects(pairs, data)
    cohorts = {r["subject"]: r["cohort"] for r in accepted}
    validation = np.array([cohorts[s] == "validation" for s in subjects])
    accepted_counts = Counter((r["subject"], r["session"], r["label"]) for r in accepted)
    paired = defaultdict(list)
    for pair in pairs:
        paired[pair["subject"], pair["session"]].append(pair)
    coverage = []
    for i, subject in enumerate(subjects):
        for j, session in enumerate(sessions):
            group = paired[subject, session]
            delays = np.array([int(p["delay_ms"]) for p in group])
            rt_gap = [abs(int(p["reactionD_ms"]) - int(p["reactionND_ms"])) for p in group]
            assert len(group) == counts[0, i, j]
            quantiles = np.percentile(delays, [5, 50, 95]) if group else [np.nan] * 3
            coverage.append(dict(
                subject=subject, session=session, cohort=cohorts[subject],
                accepted_ND=accepted_counts[subject, session, "1"],
                accepted_D=accepted_counts[subject, session, "2"],
                matched_pairs=len(group), short_pairs=int(counts[1, i, j]),
                long_pairs=int(counts[2, i, j]), median_absolute_RT_gap_ms=np.median(rt_gap) if group else np.nan,
                delay_p05_ms=quantiles[0], delay_median_ms=quantiles[1], delay_p95_ms=quantiles[2],
            ))
    write_csv(out / "match_coverage.csv", coverage)

    group_tests, participant_rows, session_rows = [], [], []
    for w, definition in enumerate(WINDOWS):
        window = window_metadata(definition)
        key, sign = window["alignment"], window["expected_sign"]
        start, end = window["start_ms"], window["end_ms_exclusive"]
        electrodes = definition["electrodes"]
        mask = (times[key] >= start) & (times[key] < end)
        assert mask.sum() == (end - start) / 2
        by_class = sums[key][mask][:, [channels.index(c) for c in electrodes], :, 0].mean(axis=(0, 1))
        all_counts = counts[0]
        by_person = by_class.sum(axis=-1) / all_counts.sum(axis=-1)
        by_session = np.divide(by_class, all_counts, out=np.full_like(by_class, np.nan),
                               where=all_counts > 0)
        for i, subject in enumerate(subjects):
            nd, d = by_person[:, i]
            meta = dict(window, subject=subject, cohort=cohorts[subject])
            interval, runs_by_session, run_based_means = repeatability[subject]
            low, high = interval[:, w]
            participant_rows.append(dict(
                meta, matched_pairs=int(all_counts[i].sum()), runs=sum(runs_by_session.values()),
                ND_uV=nd, D_uV=d, D_minus_ND_uV=d-nd,
                bootstrap95_low_uV=low, bootstrap95_high_uV=high,
                single_run_sessions=sum(count == 1 for count in runs_by_session.values()),
            ))
            for j, session in enumerate(sessions):
                if all_counts[i, j] == 0:
                    continue
                nd, d = by_session[:, i, j]
                assert np.isclose(d - nd, run_based_means[session][w], atol=1e-10, rtol=0)
                session_rows.append(dict(
                    meta, session=session, matched_pairs=int(all_counts[i, j]),
                    runs=runs_by_session[session], ND_uV=nd, D_uV=d, D_minus_ND_uV=d-nd,
                ))
        nd, d = by_person[:, validation]
        diff = d - nd
        test = ttest_1samp(diff, 0)
        se = diff.std(ddof=1) / np.sqrt(len(diff))
        lo, hi = diff.mean() + np.array([-1, 1]) * t.ppf(.975, len(diff) - 1) * se
        group_tests.append(dict(
            window, participants=len(diff), mean_ND_uV=nd.mean(), mean_D_uV=d.mean(),
            mean_D_minus_ND_uV=diff.mean(), ci95_low_uV=lo, ci95_high_uV=hi,
            participants_expected_sign=int((diff * sign > 0).sum()), t=test.statistic, p=test.pvalue,
        ))
    for row, adjusted in zip(group_tests, holm([row["p"] for row in group_tests])):
        row["p_Holm"] = adjusted
    write_csv(out / "component_tests.csv", group_tests)
    write_csv(out / "participant_component_amplitudes.csv", participant_rows)
    write_csv(out / "session_component_amplitudes.csv", session_rows)
    write_csv(out / "run_component_amplitudes.csv", run_rows)

    delay_medians = {
        group: np.median([int(r["delay_ms"]) for r in pairs
                          if r["cohort"] == "validation" and r["delayGroup"] == group])
        for group in ("short", "long")
    }
    plot_waveforms(out, times, sums, counts, channels, sessions, validation, delay_medians)
    save_report_means(out, subjects, sessions, channels, cohorts, times, sums, counts)
    print(f"{len(pairs)} matched pairs; {validation.sum()} non-pilot participants")


if __name__ == "__main__":
    main()
