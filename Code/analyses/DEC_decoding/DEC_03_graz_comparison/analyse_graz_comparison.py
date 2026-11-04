"""Matched decision-tree comparison: Graz-style r-squared selection and our bins."""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
from collections import defaultdict
import csv
import json

import numpy as np
from scipy.io import loadmat
from sklearn.metrics import confusion_matrix, roc_auc_score
from sklearn.model_selection import LeaveOneGroupOut
from sklearn.tree import DecisionTreeClassifier
from threadpoolctl import threadpool_limits

HERE = ROOT / "output/DEC_decoding/DEC_02_full_cohort_decoders"
OUT = result_path("DEC_03")
PILOT = code_path("DEC_01")
sys.path.insert(0, str(PILOT))
from analyse_decision_tree import TREE_PARAMS

CHANNELS = ["P3", "PO3", "PO7", "CP5", "CP1", "Cz", "FCz", "FC1"]
SETS = {
    "Central": [5, 6],
    "Centroparietal": [4, 3],
    "Posterior": [0, 1, 2],
    "Full": list(range(8)),
}
NAMES = {
    "DT_r2_epoch": "Top 100 r²: −1 to +1 s",
    "DT_r2_response": "Top 100 r²: 0.2–0.9 s",
    **{f"DT_{name}": f"100 ms: {name}" for name in SETS},
}
RESPONSE = np.concatenate([ch * 1000 + np.arange(600, 950) for ch in range(8)])


def read(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def measure(y, pred, score):
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    se = tp / (tp + fn) if tp + fn else np.nan
    sp = tn / (tn + fp) if tn + fp else np.nan
    return dict(
        n=len(y),
        n_ND=int(np.sum(y == 0)),
        n_D=int(np.sum(y == 1)),
        tn=int(tn),
        fp=int(fp),
        fn=int(fn),
        tp=int(tp),
        accuracy=float(np.mean(y == pred)),
        balanced_accuracy=float((se + sp) / 2),
        sensitivity_D=float(se),
        specificity_ND=float(sp),
        roc_auc=float(roc_auc_score(y, score)) if len(set(y)) == 2 else np.nan,
    )


def mean_defined(values):
    a = np.asarray(values, dtype=float)
    return float(np.mean(a[np.isfinite(a)])) if np.isfinite(a).any() else np.nan


def rank_r_squared(X, y):
    """Squared Pearson correlation, equivalent to Code/reference/rsquared.m.

    Fits on training rows only. Constant features get 0, as in the legacy
    classifier's NaN-to-zero handling. Stable ties use channel/time order.
    """
    xc = X - X.mean(axis=0)
    yc = y - y.mean()
    denominator = (yc @ yc) * np.einsum("ij,ij->j", xc, xc)
    covariance = yc @ xc
    r2 = np.divide(
        covariance**2, denominator, out=np.zeros(X.shape[1]), where=denominator > 0
    )
    assert np.isfinite(r2).all() and np.max(r2) <= 1 + 1e-10
    return np.argsort(-r2, kind="stable")[:100], r2


def main():
    OUT.mkdir(exist_ok=True)
    metadata = read(HERE / "trial_metadata.csv")
    bins = loadmat(HERE / "features.mat")["features"]
    assert bins.shape == (len(metadata), 56)
    existing = [
        r for r in read(HERE / "heldout_predictions.csv") if r["model_id"] == "DT_full"
    ]
    old = {(r["run"], int(r["trial"])): r for r in existing}
    statuses = read(HERE / "session_eligibility.csv")
    predictions, folds, summary, selected_features = [], [], [], []
    new_fits = 0
    check_error = None
    with threadpool_limits(limits=1):
        for status in statuses:
            if status["status"] != "ok":
                continue
            subject, session, cohort = (
                status["subject"],
                status["session"],
                status["cohort"],
            )
            rows = np.array(
                [
                    i
                    for i, m in enumerate(metadata)
                    if (m["subject"], m["session"]) == (subject, session)
                ]
            )
            data = loadmat(OUT / "raw_epochs" / f"{subject}_{session}.mat")
            raw = data["rawFeatures"]
            assert np.array_equal(data["globalRows"].ravel() - 1, rows)
            assert raw.shape == (len(rows), 8000) and np.isfinite(raw).all()
            assert np.allclose(data["sampleTimes"].ravel(), np.arange(-500, 500) / 500)
            y = np.array([int(metadata[i]["label"]) - 1 for i in rows])
            groups = np.array([metadata[i]["run"] for i in rows])
            splits = list(LeaveOneGroupOut().split(rows, y, groups))
            assert len(splits) == int(status["n_accepted_recordings"])
            for model_id, name in NAMES.items():
                if model_id == "DT_r2_epoch":
                    candidate = np.arange(8000)
                    X = raw
                elif model_id == "DT_r2_response":
                    candidate = RESPONSE
                    X = raw[:, candidate]
                else:
                    name_set = model_id.removeprefix("DT_")
                    columns = [ch * 7 + b for ch in SETS[name_set] for b in range(7)]
                    X = bins[rows][:, columns]
                feature_count = 100 if model_id.startswith("DT_r2") else X.shape[1]
                base = dict(
                    subject=subject,
                    session=session,
                    cohort=cohort,
                    model_id=model_id,
                    model=name,
                    n_features=feature_count,
                    n_candidates=X.shape[1],
                )
                pred_all = np.full(len(rows), -1)
                score_all = np.full(len(rows), np.nan)
                seen = np.zeros(len(rows), dtype=int)
                current = []
                for train, test in splits:
                    assert not set(groups[train]) & set(groups[test])
                    assert set(y[train]) == {0, 1}
                    run = str(groups[test][0])
                    if model_id == "DT_Full":
                        saved = [
                            old[metadata[i]["run"], int(metadata[i]["trial"])]
                            for i in rows[test]
                        ]
                        assert [int(r["true_D"]) for r in saved] == y[test].tolist()
                        pred = np.array([int(r["predicted_D"]) for r in saved])
                        score = np.array([float(r["score"]) for r in saved])
                    else:
                        if model_id.startswith("DT_r2"):
                            keep, r2 = rank_r_squared(X[train], y[train])
                            if check_error is None:
                                columns = np.unique(np.r_[keep[:8], np.arange(8)])
                                direct = np.array(
                                    [
                                        (
                                            np.corrcoef(X[train, col], y[train])[0, 1]
                                            ** 2
                                            if np.std(X[train, col]) > 0
                                            else 0
                                        )
                                        for col in columns
                                    ]
                                )
                                check_error = float(
                                    np.max(np.abs(direct - r2[columns]))
                                )
                                assert check_error < 1e-12
                            for rank, col in enumerate(keep, 1):
                                original = int(candidate[col])
                                ch, sample = divmod(original, 1000)
                                selected_features.append(
                                    dict(
                                        subject=subject,
                                        session=session,
                                        cohort=cohort,
                                        model_id=model_id,
                                        heldout_run=run,
                                        rank=rank,
                                        feature_index_zero_based=original,
                                        channel=CHANNELS[ch],
                                        time_seconds=(sample - 500) / 500,
                                        r_squared=float(r2[col]),
                                        n_train=len(train),
                                    )
                                )
                        else:
                            keep = np.arange(X.shape[1])
                        model = DecisionTreeClassifier(**TREE_PARAMS)
                        model.fit(X[train][:, keep], y[train])
                        pred = model.predict(X[test][:, keep])
                        score = model.predict_proba(X[test][:, keep])[:, 1]
                        new_fits += 1
                    assert np.isfinite(score).all()
                    pred_all[test], score_all[test] = pred, score
                    seen[test] += 1
                    result = measure(y[test], pred, score)
                    row = dict(**base, heldout_run=run, n_train=len(train), **result)
                    folds.append(row)
                    current.append(row)
                    for local, predicted, probability in zip(test, pred, score):
                        m = metadata[rows[local]]
                        predictions.append(
                            dict(
                                **base,
                                run=m["run"],
                                trial=int(m["trial"]),
                                original_label=int(m["label"]),
                                true_D=int(y[local]),
                                predicted_D=int(predicted),
                                probability_D=float(probability),
                            )
                        )
                assert np.all(seen == 1) and np.isfinite(score_all).all()
                result = measure(y, pred_all, score_all)
                result["pooled_oof_roc_auc"] = result.pop("roc_auc")
                result["mean_run_roc_auc"] = mean_defined(
                    [r["roc_auc"] for r in current]
                )
                result["runs_with_defined_auc"] = sum(
                    np.isfinite(r["roc_auc"]) for r in current
                )
                result["mean_run_balanced_accuracy"] = mean_defined(
                    [r["balanced_accuracy"] for r in current]
                )
                summary.append(dict(**base, n_runs=len(splits), **result))
            print(
                f"{cohort} {subject}/{session}: all six tree feature designs complete",
                flush=True,
            )
    assert len(predictions) == 181260 and len(folds) == 2094 and new_fits == 1745
    assert len(selected_features) == 69800 and len(summary) == 438
    assert len({(r["run"], r["trial"], r["model_id"]) for r in predictions}) == len(
        predictions
    )
    write("heldout_predictions.csv", predictions)
    write("fold_metrics.csv", folds)
    write("session_metrics.csv", summary)
    write("selected_features.csv", selected_features)
    settings = dict(
        tree_parameters=TREE_PARAMS,
        selection="Training-fold squared Pearson correlation; "
        "top 100, stable ties, constant features scored zero",
        legacy_reference="Code/reference/rsquared.m",
        pearson_check_max_error=check_error,
        raw_epoch_interval="[-1,+1) s, 1000 samples/channel, 8000 candidates",
        raw_response_interval="[0.2,0.9) s, 350 samples/channel, 2800 candidates",
        bin_interval="[0.2,0.9) s, seven 100 ms means/channel",
        channel_sets={
            name: [CHANNELS[i] for i in indices] for name, indices in SETS.items()
        },
        model_names=NAMES,
        preprocessing="Unchanged primary full-dataset no-FORCe pipeline",
        validation="Identical existing participant/session-specific whole-run holdouts and accepted IDs",
        paper_interval_note="Paper documents [-1,+1] s epochs but no separate classification interval; "
        "full-epoch selection is an explicit interpretation",
        differences_from_paper=[
            "No FORCe; existing fourth-order analysis filter",
            "Whole-run holdouts rather than reported 10-fold CV",
            "Sessions separate; participant weighting after session summaries",
            "Explicit fixed tree defaults because published hyperparameters unspecified",
        ],
        tuning="None; feature ranking is fitted on training folds only",
        new_fits=new_fits,
        reused_Full_bin_folds=349,
        comparison_folds=len(folds),
        prediction_rows=len(predictions),
    )
    (OUT / "analysis_settings.json").write_text(
        json.dumps(settings, indent=2), encoding="utf-8"
    )
    summarise(summary)
    print(
        f"GRAZ COMPARISON COMPLETE: {new_fits} new fits, 349 reused Full-bin folds; {len(predictions)} predictions.",
        flush=True,
    )


def summarise(sessions):
    groups = defaultdict(list)
    for r in sessions:
        groups[r["subject"], r["cohort"], r["model_id"]].append(r)
    participant = []
    keys = [
        "balanced_accuracy",
        "accuracy",
        "sensitivity_D",
        "specificity_ND",
        "mean_run_roc_auc",
    ]
    for (subject, cohort, model), rows in groups.items():
        participant.append(
            dict(
                subject=subject,
                cohort=cohort,
                model_id=model,
                model=NAMES[model],
                n_sessions=len(rows),
                **{k: mean_defined([r[k] for r in rows]) for k in keys},
            )
        )
    write("participant_metrics.csv", participant)
    aggregate = []
    for cohort in ["validation", "pilot"]:
        for model in NAMES:
            rows = [
                r
                for r in participant
                if (r["cohort"], r["model_id"]) == (cohort, model)
            ]
            aggregate.append(
                dict(
                    cohort=cohort,
                    model_id=model,
                    model=NAMES[model],
                    n_participants=len(rows),
                    n_sessions=sum(r["n_sessions"] for r in rows),
                    **{f"mean_{k}": mean_defined([r[k] for r in rows]) for k in keys},
                )
            )
    write("cohort_summary.csv", aggregate)
    for r in aggregate:
        print(
            r["cohort"],
            r["model_id"],
            f"BA={r['mean_balanced_accuracy']:.3f}, AUC={r['mean_mean_run_roc_auc']:.3f}",
            flush=True,
        )
    lookup = {(r["subject"], r["model_id"]): r for r in participant}
    paired = []
    for subject in sorted({r["subject"] for r in participant}):
        reference = lookup[subject, "DT_Full"]
        for model in NAMES:
            if model == "DT_Full":
                continue
            r = lookup[subject, model]
            paired.append(
                dict(
                    subject=subject,
                    cohort=r["cohort"],
                    model_id=model,
                    delta_BA_minus_Full_bins=r["balanced_accuracy"]
                    - reference["balanced_accuracy"],
                    delta_AUC_minus_Full_bins=r["mean_run_roc_auc"]
                    - reference["mean_run_roc_auc"],
                )
            )
    write("paired_participant_differences.csv", paired)
    plot(participant)
    build_readme(aggregate)


def plot(participant):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    models = list(NAMES)
    subjects = sorted(
        {r["subject"] for r in participant if r["cohort"] == "validation"}
    )
    lookup = {(r["subject"], r["model_id"]): r for r in participant}
    reference = [
        r
        for r in read(HERE / "cohort_summary.csv")
        if r["cohort"] == "validation" and r["model_id"] == "LDA_full"
    ][0]
    fig, axes = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True, constrained_layout=True
    )
    for ax, metric, title in zip(
        axes,
        ["balanced_accuracy", "mean_run_roc_auc"],
        ["Balanced accuracy", "Mean held-out-run ROC-AUC"],
    ):
        values = np.array([[lookup[s, m][metric] for m in models] for s in subjects])
        for row in values:
            ax.plot(
                range(6), row, "o-", color=".55", alpha=0.3, markersize=3, linewidth=0.6
            )
        ax.plot(
            range(6),
            values.mean(axis=0),
            "D-",
            color="#1b5e91",
            markersize=7,
            linewidth=2,
            label="Equal-participant mean",
        )
        ax.axhline(
            float(reference["mean_" + metric]),
            color="#36998d",
            linestyle="--",
            label="Existing full-montage LDA mean",
        )
        ax.axhline(0.5, color=".4", linestyle=":", linewidth=0.8)
        ax.set_ylim(0.3, 1.01)
        ax.set_ylabel(title)
        ax.grid(axis="y", alpha=0.2)
        ax.set_xticks(
            range(6),
            [
                "r² top 100\n−1 to +1 s",
                "r² top 100\n0.2–0.9 s",
                "100 ms\nCentral",
                "100 ms\nCentroparietal",
                "100 ms\nPosterior",
                "100 ms\nFull",
            ],
        )
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=2)
    fig.suptitle(
        "Decision trees | 23 validation participants | Same no-FORCe trials and held-out runs\nGrey lines: participant means across eligible sessions"
    )
    fig.savefig(OUT / "feature_design_comparison.png", dpi=180)
    plt.close(fig)


def build_readme(aggregate):
    lines = [
        "# Graz-style amplitude selection versus our decision-tree feature sets",
        "",
        "## What the paper specifies",
        "",
        "The Graz paper reports movement-locked epochs spanning [−1,+1] s, a binary "
        "decision tree, and 100 channel/time-point amplitude features ranked by r-squared "
        "using each fold's training data. It does **not** state that classification was "
        "restricted to [0.2,0.9) s. Nor does it separately state the precise classification "
        "candidate interval. Using all samples in its documented two-second epoch is "
        "therefore our explicit full-epoch interpretation, not a recovered implementation detail.",
        "",
        "The 100 features are 100 **channel/time-point pairs**. They need not represent "
        "100 unique clock times, and they are not time-bin averages.",
        "",
        "## Matched comparison",
        "",
        "| Tree feature design | Candidate pool | Inputs to tree |",
        "|---|---|---:|",
        "| Graz-style full epoch | 8 channels × 1000 samples, [−1,+1) s | Training-fold top 100 |",
        "| Same-interval amplitude control | 8 channels × 350 samples, [0.2,0.9) s | Training-fold top 100 |",
        "| Central bins: Cz, FCz | Seven 100 ms means/channel, [0.2,0.9) s | 14 |",
        "| Centroparietal bins: CP1, CP5 | Same seven bins/channel | 14 |",
        "| Posterior bins: P3, PO3, PO7 | Same seven bins/channel | 21 |",
        "| Full montage bins | Same seven bins, all eight channels | 56 |",
        "",
        "R-squared is squared Pearson correlation with the binary class label, matching "
        "`Code/reference/rsquared.m`. Constant features receive zero, consistent "
        "with the legacy classifier's undefined-score handling. Feature ranking is "
        "recomputed from training trials separately in every fold; the test recording "
        "does not influence ranking, means or thresholds. Ties use fixed channel/time order. "
        "An independent Pearson calculation checks the vectorised ranking implementation.",
        "",
        "All six designs use the exact accepted no-FORCe trial IDs, existing session "
        "eligibility decisions and whole-recording holdouts from the full-dataset analysis. "
        "All use the same fixed Gini CART settings, no pruning or class weighting and "
        "random seed 20261027. There is no tuning. The Full-bin tree predictions are reused "
        "exactly; the other five designs are new fits. This isolates the feature-design "
        "comparison within a fixed tree/evaluation setup.",
        "",
        "There are 30,210 evaluated trials across 73 participant/sessions, 2,094 comparison "
        "folds, 1,745 new tree fits, 349 reused Full-bin folds and 181,260 held-out predictions. "
        "The 23 validation participants are reported separately from the two pilots. "
        "The two previously excluded pre sessions remain excluded; no new trial filtering "
        "or preprocessing is performed.",
        "",
        "## Validation results",
        "",
        "Metrics are averaged across eligible sessions within each participant, then "
        "participants equally. Session BA uses all held-out confusion counts; AUC averages "
        "defined two-class held-out-run AUCs.",
        "",
        "| Feature design | Accuracy | BA | D sensitivity | ND specificity | AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in aggregate:
        if r["cohort"] != "validation":
            continue
        lines.append(
            f"| {r['model']} | "
            + " | ".join(
                f"{r['mean_'+k]:.3f}"
                for k in [
                    "accuracy",
                    "balanced_accuracy",
                    "sensitivity_D",
                    "specificity_ND",
                    "mean_run_roc_auc",
                ]
            )
            + " |"
        )
    lines += [
        "",
        "The [previous full-dataset LDA results](../DEC_02_full_cohort_decoders/README.md) remain unchanged. "
        "The comparison figure includes their full-montage mean as a reference; "
        "class handling differs between that LDA and these trees.",
        "",
        "## Pilot results, separate",
        "",
        "| Feature design | BA | AUC |",
        "|---|---:|---:|",
    ]
    for r in aggregate:
        if r["cohort"] == "pilot":
            lines.append(
                f"| {r['model']} | {r['mean_balanced_accuracy']:.3f} | {r['mean_mean_run_roc_auc']:.3f} |"
            )
    lines += [
        "",
        "## Interpretation",
        "",
        "- Compare full-epoch and response-interval r-squared models to assess the "
        "candidate-interval choice under the same selection rule. The response-interval "
        "r-squared control and our bins share [0.2,0.9), allowing a closer feature-method "
        "comparison. The number of inputs still differs: 100 selected amplitudes versus "
        "14–56 bin means.",
        "- This is a Graz-style feature-selection and classifier comparison, not an exact "
        "reproduction of its published scores. We retain no-FORCe preprocessing, a "
        "fourth-order filter, session-specific whole-run holdouts and explicit tree "
        "defaults. The paper used FORCe, a third-order filter and reported 10-fold CV; "
        "tree hyperparameters were not specified.",
        "- Models remain personalised. This does not test transfer of a trained model "
        "to another participant/session or establish a neural ErrP source. Results are "
        "descriptive; no new hyperparameters are chosen from these scores.",
        "- Selected samples can be adjacent and strongly correlated. Selection frequency "
        "across overlapping training folds is not independent evidence for a component "
        "latency or cortical source. Full-epoch features can include pre-onset samples.",
        "- These additional feature designs are follow-up exploratory comparisons on the "
        "same validation cohort; their results do not create a new untouched test set.",
        "",
        "## Files and reproduction",
        "",
        "- `cohort_summary.csv`, `participant_metrics.csv`, `session_metrics.csv`, "
        "`fold_metrics.csv`: results at each level.",
        "- `heldout_predictions.csv`: all six designs with identical trial/label IDs.",
        "- `selected_features.csv`: each selected channel, time, rank and training r-squared "
        "for both raw-amplitude models, separately for every held-out run.",
        "- `paired_participant_differences.csv`: differences from the Full-bin tree.",
        "- `analysis_settings.json`: exact assumptions, settings and verification.",
        "- `feature_design_comparison.png`: participant-wise and mean validation scores.",
        "",
        "",
        "",
        "Source: [Graz paper, Data Analysis and Evaluation](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf).",
        "",
    ]
    (OUT / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
