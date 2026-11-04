"""Extend the fixed LDA pilot to every audited channel set.

Preserves the original results and reuses their Central predictions. Other
channel sets use exactly the same trial IDs, run holdouts and LDA settings.
"""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv
import json
import time
import warnings

import numpy as np
from scipy.io import loadmat
from sklearn.model_selection import LeaveOneGroupOut
from threadpoolctl import threadpool_limits

from analyse_classification import (
    make_lda,
    metrics,
    CONDITIONS,
    REPRESENTATIONS,
    SUBJECTS,
    SESSIONS,
)

HERE = ROOT / "output/DEC_decoding/DEC_01_pilot_decoders"
OUT = HERE / "channel_sets"
CHANNELS = ["P3", "PO3", "PO7", "CP5", "CP1", "Cz", "FCz", "FC1"]
SETS = {
    "Central": ["Cz", "FCz"],
    "Centroparietal": ["CP1", "CP5"],
    "Posterior": ["P3", "PO3", "PO7"],
    "Full": CHANNELS,
}


def read(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    OUT.mkdir(exist_ok=True)
    metadata = read(HERE / "trial_metadata.csv")
    mat = loadmat(HERE / "all_channel_features.mat")
    raw = mat["allFeatures"]
    n = len(metadata)
    assert n == 2562 and raw.shape == (n, 350, 8, 4) and np.isfinite(raw).all()
    assert [str(x.item()) for x in mat["allChannels"].ravel()] == CHANNELS
    central_export = loadmat(HERE / "central_features.mat")["rawFeatures"]
    for c in CONDITIONS:
        actual = raw[:, :, [5, 6], c - 1].transpose(0, 2, 1).reshape(n, 700)
        assert np.array_equal(actual, central_export[:, :, c - 1])
    del central_export
    yall = np.array([int(m["label"]) - 1 for m in metadata])
    old = {
        (r["run"], int(r["trial"]), int(r["condition_id"]), r["representation"]): r
        for r in read(HERE / "heldout_predictions.csv")
    }
    old_summary = {
        (r["subject"], r["session"], int(r["condition_id"]), r["representation"]): r
        for r in read(HERE / "session_metrics.csv")
    }
    predictions, folds, sessions = [], [], []
    actual_fits = 0
    start = time.perf_counter()
    with threadpool_limits(limits=1), warnings.catch_warnings():
        warnings.simplefilter("error")
        for subject in SUBJECTS:
            for session in SESSIONS:
                selected = np.array(
                    [
                        i
                        for i, m in enumerate(metadata)
                        if (m["subject"], m["session"]) == (subject, session)
                    ]
                )
                y = yall[selected]
                groups = np.array([metadata[i]["run"] for i in selected])
                splits = list(LeaveOneGroupOut().split(selected, y, groups))
                for cid, condition in CONDITIONS.items():
                    for channel_set, channels in SETS.items():
                        channel_indices = [CHANNELS.index(ch) for ch in channels]
                        z = raw[selected, :, :, cid - 1][
                            :, :, channel_indices
                        ].transpose(0, 2, 1)
                        for rep, width in REPRESENTATIONS.items():
                            X = (
                                z.reshape(
                                    len(selected), len(channels), 350 // width, width
                                )
                                .mean(axis=-1)
                                .reshape(len(selected), -1)
                            )
                            oof_pred = np.full(len(selected), -1)
                            oof_score = np.full(len(selected), np.nan)
                            seen = np.zeros(len(selected), dtype=int)
                            config_folds = []
                            for train, test in splits:
                                assert not set(groups[train]) & set(groups[test])
                                assert len(set(groups[test])) == 1
                                assert set(y[train]) == set(y[test]) == {0, 1}
                                if channel_set == "Central":
                                    saved = [
                                        old[
                                            metadata[i]["run"],
                                            int(metadata[i]["trial"]),
                                            cid,
                                            rep,
                                        ]
                                        for i in selected[test]
                                    ]
                                    assert [int(r["true_D"]) for r in saved] == y[
                                        test
                                    ].tolist()
                                    pred = np.array(
                                        [int(r["predicted_D"]) for r in saved]
                                    )
                                    score = np.array(
                                        [float(r["decision_score"]) for r in saved]
                                    )
                                else:
                                    model = make_lda()
                                    model.fit(X[train], y[train])
                                    assert np.allclose(
                                        model[0].mean_, X[train].mean(axis=0)
                                    )
                                    pred = model.predict(X[test])
                                    score = model.decision_function(X[test])
                                    actual_fits += 1
                                assert np.isfinite(score).all()
                                oof_pred[test], oof_score[test] = pred, score
                                seen[test] += 1
                                base = dict(
                                    subject=subject,
                                    session=session,
                                    condition_id=cid,
                                    condition=condition,
                                    channel_set=channel_set,
                                    channels="+".join(channels),
                                    representation=rep,
                                    n_features=X.shape[1],
                                    prediction_source=(
                                        "reused central LDA"
                                        if channel_set == "Central"
                                        else "new fit"
                                    ),
                                )
                                result = dict(
                                    **base,
                                    heldout_run=str(groups[test][0]),
                                    n_train=len(train),
                                    train_ND=int(np.sum(y[train] == 0)),
                                    train_D=int(np.sum(y[train] == 1)),
                                    **metrics(y[test], pred, score),
                                    accuracy=float(np.mean(y[test] == pred)),
                                )
                                folds.append(result)
                                config_folds.append(result)
                                for local, predicted, decision in zip(
                                    test, pred, score
                                ):
                                    m = metadata[selected[local]]
                                    predictions.append(
                                        dict(
                                            **base,
                                            run=m["run"],
                                            run_number=int(m["runNumber"]),
                                            trial=int(m["trial"]),
                                            original_label=int(m["label"]),
                                            true_D=int(y[local]),
                                            predicted_D=int(predicted),
                                            decision_score=float(decision),
                                        )
                                    )
                            assert np.all(seen == 1) and np.isfinite(oof_score).all()
                            result = metrics(y, oof_pred, oof_score)
                            result["pooled_oof_roc_auc"] = result.pop("roc_auc")
                            result["accuracy"] = float(np.mean(y == oof_pred))
                            result["mean_run_roc_auc"] = float(
                                np.mean([r["roc_auc"] for r in config_folds])
                            )
                            result["mean_run_balanced_accuracy"] = float(
                                np.mean([r["balanced_accuracy"] for r in config_folds])
                            )
                            result["min_run_balanced_accuracy"] = min(
                                r["balanced_accuracy"] for r in config_folds
                            )
                            result["max_run_balanced_accuracy"] = max(
                                r["balanced_accuracy"] for r in config_folds
                            )
                            if channel_set == "Central":
                                reference = old_summary[subject, session, cid, rep]
                                for key in [
                                    "balanced_accuracy",
                                    "mean_run_roc_auc",
                                    "sensitivity_D",
                                    "specificity_ND",
                                ]:
                                    assert (
                                        abs(result[key] - float(reference[key])) < 1e-12
                                    )
                            sessions.append(dict(**base, n_runs=len(splits), **result))
                            print(
                                f"{subject}/{session} C{cid} {channel_set} {rep} ({X.shape[1]} features): "
                                f'BA={result["balanced_accuracy"]:.3f}, AUC={result["mean_run_roc_auc"]:.3f}; '
                                f"elapsed={time.perf_counter()-start:.0f}s",
                                flush=True,
                            )
    assert actual_fits == 1044 and len(folds) == 1392 and len(sessions) == 288
    assert len(predictions) == n * 48 == 122976
    keys = {
        (r["run"], r["trial"], r["condition_id"], r["channel_set"], r["representation"])
        for r in predictions
    }
    assert len(keys) == len(predictions)
    write("heldout_predictions.csv", predictions)
    write("fold_metrics.csv", folds)
    write("session_metrics.csv", sessions)
    lookup = {
        (
            r["subject"],
            r["session"],
            r["condition_id"],
            r["channel_set"],
            r["representation"],
            r["heldout_run"],
        ): r
        for r in folds
    }
    paired = []
    for r in folds:
        if r["channel_set"] == "Central":
            continue
        ref = lookup[
            r["subject"],
            r["session"],
            r["condition_id"],
            "Central",
            r["representation"],
            r["heldout_run"],
        ]
        assert (r["n"], r["n_D"], r["n_train"]) == (
            ref["n"],
            ref["n_D"],
            ref["n_train"],
        )
        paired.append(
            dict(
                subject=r["subject"],
                session=r["session"],
                condition_id=r["condition_id"],
                channel_set=r["channel_set"],
                representation=r["representation"],
                heldout_run=r["heldout_run"],
                **{
                    f"delta_{key}_minus_Central": r[key] - ref[key]
                    for key in [
                        "balanced_accuracy",
                        "roc_auc",
                        "sensitivity_D",
                        "specificity_ND",
                    ]
                },
            )
        )
    write("paired_channel_differences.csv", paired)
    settings = json.loads((HERE / "analysis_settings.json").read_text(encoding="utf-8"))
    settings.update(
        channel_sets=SETS,
        channels=CHANNELS,
        representations={
            rep: {
                group: len(channels) * (350 // width)
                for group, channels in SETS.items()
            }
            for rep, width in REPRESENTATIONS.items()
        },
        fits=actual_fits,
        reused_central_folds=348,
        comparison_folds=len(folds),
        prediction_rows=len(predictions),
        configurations=48,
        tuning="No hyperparameter search or channel selection inside this exploratory comparison",
        selection_note="The candidate groups were predefined during the audit. Scores compare them within the same pilots, "
        "not independent confirmation of a selected group.",
        primary_condition=1,
    )
    (OUT / "analysis_settings.json").write_text(
        json.dumps(settings, indent=2), encoding="utf-8"
    )
    summarise(sessions, folds)
    print(
        f"CHANNEL-SET CLASSIFICATION COMPLETE: {actual_fits} new fits, 348 reused Central folds, "
        f"{len(predictions)} predictions.",
        flush=True,
    )


def summarise(sessions, folds):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    groups = [(s, v) for s in SUBJECTS for v in SESSIONS]
    reps = list(REPRESENTATIONS)
    lookup = {
        (
            r["subject"],
            r["session"],
            r["condition_id"],
            r["channel_set"],
            r["representation"],
        ): r
        for r in sessions
    }
    aggregate = []
    for cid in CONDITIONS:
        for name in SETS:
            for rep in reps:
                rows = [
                    r
                    for r in sessions
                    if (r["condition_id"], r["channel_set"], r["representation"])
                    == (cid, name, rep)
                ]
                aggregate.append(
                    dict(
                        condition_id=cid,
                        condition=CONDITIONS[cid],
                        channel_set=name,
                        representation=rep,
                        n_features=rows[0]["n_features"],
                        **{
                            f"mean_session_{key}": float(
                                np.mean([r[key] for r in rows])
                            )
                            for key in [
                                "balanced_accuracy",
                                "mean_run_roc_auc",
                                "sensitivity_D",
                                "specificity_ND",
                            ]
                        },
                    )
                )
    write("descriptive_pilot_summary.csv", aggregate)
    columns = [(name, rep) for name in SETS for rep in reps]
    fig, axes = plt.subplots(2, 1, figsize=(15, 8), constrained_layout=True)
    for ax, metric, title in zip(
        axes,
        ["balanced_accuracy", "mean_run_roc_auc"],
        ["Balanced accuracy", "Mean held-out-run ROC-AUC"],
    ):
        values = np.array(
            [
                [lookup[s, v, 1, name, rep][metric] for name, rep in columns]
                for s, v in groups
            ]
        )
        im = ax.imshow(values, vmin=0.4, vmax=1, cmap="YlGnBu", aspect="auto")
        ax.set_yticks(range(6), [f"{s} / {v}" for s, v in groups])
        ax.set_xticks(
            range(12), [f"{name}\n{rep}" for name, rep in columns], fontsize=8
        )
        ax.set_title(title, loc="left", fontweight="bold")
        for i in range(6):
            for j in range(12):
                ax.text(
                    j,
                    i,
                    f"{values[i,j]:.3f}",
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white" if values[i, j] > 0.82 else "black",
                )
        for x in [2.5, 5.5, 8.5]:
            ax.axvline(x, color="white", linewidth=3)
        ax.axhline(2.5, color="white", linewidth=3)
        fig.colorbar(im, ax=ax, shrink=0.85)
    fig.suptitle(
        "Primary BP no-FORCe | All audited channel sets | Matched whole-run holdouts"
    )
    fig.savefig(OUT / "primary_channel_comparison.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(
        2, 3, figsize=(13, 7), constrained_layout=True, sharey=True
    )
    colors = {1: "#1b5e91", 2: "#d27912", 3: "#36998d", 4: "#a14375"}
    for ax, (s, v) in zip(axes.ravel(), groups):
        for cid in CONDITIONS:
            scores = [
                lookup[s, v, cid, name, "100ms"]["balanced_accuracy"] for name in SETS
            ]
            ax.plot(range(4), scores, "-o", label=CONDITIONS[cid], color=colors[cid])
        ax.set_title(f"{s} / {v}")
        ax.set_xticks(
            range(4), ["Central", "Centro-\nparietal", "Posterior", "Full"], fontsize=9
        )
        ax.axhline(0.5, color=".5", linestyle="--", linewidth=0.8)
        ax.set_ylim(0.35, 1)
        ax.grid(axis="y", alpha=0.2)
    for ax in axes[:, 0]:
        ax.set_ylabel("Balanced accuracy")
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=4)
    fig.suptitle(
        "100 ms features | All four processing conditions | Same trials and run holdouts"
    )
    fig.savefig(OUT / "all_conditions_100ms.png", dpi=180)
    plt.close(fig)
    lines = [
        "# LDA comparison of all audited channel sets",
        "",
        "## Fixed analysis",
        "",
        "The original shrinkage-LDA comparison is extended to every channel set from the "
        "feature audit. All 2,562 matched trial IDs, four processing conditions, three temporal "
        "representations and participant/session-specific whole-run holdouts are retained. "
        "Condition 1, BP no-FORCe, is the primary analysis. Other conditions are sensitivity comparisons.",
        "",
        "| Channel set | Channels | 100 ms features | 50 ms features | Sample features |",
        "|---|---|---:|---:|---:|",
    ]
    for name, channels in SETS.items():
        lines.append(
            f'| {name} | {", ".join(channels)} | {7*len(channels)} | {14*len(channels)} | {350*len(channels)} |'
        )
    lines += [
        "",
        "All representations cover [0.2, 0.9) s. The sample representation uses the original "
        "500 Hz samples. Each channel contributes its own features; no channel averaging is used.",
        "",
        'The shared model is training-fold StandardScaler followed by LDA with solver="lsqr", '
        'shrinkage="auto" and equal class priors. No tuning or feature selection is introduced. '
        "Central predictions are reused from the original analysis after verifying that the "
        "new export is sample-identical. The other three groups require 1,044 new fits. "
        "There are 1,392 comparison folds, 288 participant/session configurations and 122,976 "
        "held-out predictions. Each configuration predicts every matched trial once.",
        "",
        "## Primary no-FORCe results",
        "",
        "**100 ms balanced accuracy**, from pooled held-out confusion counts in each session:",
        "",
        "| Participant / session | Central | Centroparietal | Posterior | Full |",
        "|---|---:|---:|---:|---:|",
    ]
    for s, v in groups:
        lines.append(
            f"| {s} / {v} | "
            + " | ".join(
                f"{lookup[s,v,1,name,'100ms']['balanced_accuracy']:.3f}"
                for name in SETS
            )
            + " |"
        )
    lines += [
        "",
        "Descriptive mean BA / mean run-AUC across the six participant/session results:",
        "",
        "| Channel set | 100 ms | 50 ms | Samples |",
        "|---|---:|---:|---:|",
    ]
    for name in SETS:
        cells = []
        for rep in reps:
            r = next(
                r
                for r in aggregate
                if (r["condition_id"], r["channel_set"], r["representation"])
                == (1, name, rep)
            )
            cells.append(
                f"{r['mean_session_balanced_accuracy']:.3f} / {r['mean_session_mean_run_roc_auc']:.3f}"
            )
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    primary_100 = {
        name: next(
            r
            for r in aggregate
            if (r["condition_id"], r["channel_set"], r["representation"])
            == (1, name, "100ms")
        )
        for name in SETS
    }
    best_group = max(
        SETS, key=lambda name: primary_100[name]["mean_session_balanced_accuracy"]
    )
    full_wins = sum(
        lookup[s, v, 1, "Full", "100ms"]["balanced_accuracy"]
        > lookup[s, v, 1, "Central", "100ms"]["balanced_accuracy"]
        for s, v in groups
    )
    lines += [
        "",
        "## Pilot finding",
        "",
        f"At 100 ms, {best_group} has the highest descriptive mean balanced accuracy. "
        f"Full is higher than Central in {full_wins}/6 participant/session analyses: "
        f"{100*primary_100['Full']['mean_session_balanced_accuracy']:.1f}% versus "
        f"{100*primary_100['Central']['mean_session_balanced_accuracy']:.1f}% on average. "
        "The smaller-set waveform audit therefore does not establish that Central is the "
        "best decoder channel set. The full 56-feature representation should remain a "
        "candidate for subsequent independent evaluation.",
    ]
    lines += [
        "",
        "## Interpretation and limits",
        "",
        "- Group comparisons use identical held-out trials and runs. Differences in feature "
        "count are part of the predefined channel-set comparison; no additional feature-count "
        "matching or optimisation is attempted.",
        "- Balanced accuracy is the mean of displaced sensitivity and non-displaced specificity. "
        "AUC is computed within held-out runs then averaged, because separately fitted models "
        "may use different score scales. Both class recalls, confusion counts, run scores and "
        "overall accuracy are saved.",
        "- Candidate sets were defined after examining these pilot waveforms. Held-out-run "
        "scores help choose a practical baseline within the pilot; confirming that choice "
        "requires independent sessions or participants. Selecting the highest score here "
        "does not create an unbiased estimate of its future performance.",
        "- The full montage adds FC1 as well as centroparietal and posterior channels. An "
        "advantage for Full would not attribute the gain to posterior electrodes alone. "
        "Multichannel covariance can add predictive information even when single-channel "
        "average-waveform separation is smaller.",
        "- Better classification does not identify a cortical source or establish that the "
        "predictive information is specifically a neural ErrP. No population significance "
        "claim is made from two participants.",
        "- The decision-tree experiment remains a separate, Central-only comparison. This "
        "extension does not add a new tree benchmark.",
        "",
        "## Reproduction and outputs",
        "",
        "Run the extended `export_central_features.m` once in MATLAB, then run "
        "`python "
        "Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_channel_sets.py` from the repository root. "
        "The original Central and decision-tree results are preserved.",
        "",
        "- `session_metrics.csv`: all 288 results, including class recalls and confusion counts.",
        "- `fold_metrics.csv`: all 1,392 identical-run comparison rows.",
        "- `heldout_predictions.csv`: individual predictions, IDs, scores and channel-set metadata.",
        "- `paired_channel_differences.csv`: same-fold differences from Central.",
        "- `descriptive_pilot_summary.csv`: means by condition, channel set and representation.",
        "- `analysis_settings.json`: exact groups, inherited model settings and trial-selection protocol.",
        "- `primary_channel_comparison.png`: all primary-condition scores.",
        "- `all_conditions_100ms.png`: all processing conditions at 100 ms.",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
