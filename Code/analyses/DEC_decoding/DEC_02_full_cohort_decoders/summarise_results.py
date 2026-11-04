"""Participant-weighted summaries and plots for the fixed decoder evaluation."""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
from collections import defaultdict, Counter
import csv
import numpy as np

HERE = ROOT / "output/DEC_decoding/DEC_02_full_cohort_decoders"
NAMES = {
    "LDA_full": "LDA, all eight",
    "LDA_central": "LDA, Cz/FCz",
    "DT_full": "Decision tree, all eight",
}
COLORS = {"LDA_full": "#1b5e91", "LDA_central": "#36998d", "DT_full": "#b46222"}
METRICS = [
    "balanced_accuracy",
    "accuracy",
    "sensitivity_D",
    "specificity_ND",
    "mean_run_roc_auc",
]


def write(name, rows):
    with (HERE / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def read(name):
    with (HERE / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def summarise(sessions, folds, statuses):
    participant = []
    group = defaultdict(list)
    for r in sessions:
        group[r["subject"], r["cohort"], r["model_id"]].append(r)
    for (subject, cohort, model), rows in group.items():
        participant.append(
            dict(
                subject=subject,
                cohort=cohort,
                model_id=model,
                model=NAMES[model],
                n_sessions=len(rows),
                n_trials=sum(r["n"] for r in rows),
                n_recordings=sum(r["n_runs"] for r in rows),
                **{key: float(np.nanmean([r[key] for r in rows])) for key in METRICS},
            )
        )
    write("participant_metrics.csv", participant)
    cohort = []
    for name in ["validation", "pilot"]:
        for model in NAMES:
            rows = [
                r for r in participant if (r["cohort"], r["model_id"]) == (name, model)
            ]
            cohort.append(
                dict(
                    cohort=name,
                    model_id=model,
                    model=NAMES[model],
                    n_participants=len(rows),
                    n_sessions=sum(r["n_sessions"] for r in rows),
                    n_trials=sum(r["n_trials"] for r in rows),
                    **{
                        f"mean_{key}": float(np.nanmean([r[key] for r in rows]))
                        for key in METRICS
                    },
                    median_balanced_accuracy=float(
                        np.median([r["balanced_accuracy"] for r in rows])
                    ),
                    min_balanced_accuracy=min(r["balanced_accuracy"] for r in rows),
                    max_balanced_accuracy=max(r["balanced_accuracy"] for r in rows),
                )
            )
    write("cohort_summary.csv", cohort)
    lookup = {(r["subject"], r["model_id"]): r for r in participant}
    paired = []
    for subject in sorted({r["subject"] for r in participant}):
        full = lookup[subject, "LDA_full"]
        central = lookup[subject, "LDA_central"]
        tree = lookup[subject, "DT_full"]
        paired.append(
            dict(
                subject=subject,
                cohort=full["cohort"],
                n_sessions=full["n_sessions"],
                delta_BA_full_minus_central=full["balanced_accuracy"]
                - central["balanced_accuracy"],
                delta_AUC_full_minus_central=full["mean_run_roc_auc"]
                - central["mean_run_roc_auc"],
                delta_BA_tree_minus_LDA_full=tree["balanced_accuracy"]
                - full["balanced_accuracy"],
            )
        )
    write("paired_participant_differences.csv", paired)
    ret = read("retention_by_run.csv")
    ret_groups = defaultdict(list)
    for r in ret:
        ret_groups[r["subject"], r["session"], r["cohort"]].append(r)
    retention = []
    for (subject, session, cohort_name), rows in ret_groups.items():
        retention.append(
            dict(
                subject=subject,
                session=session,
                cohort=cohort_name,
                n_recordings=len(rows),
                n_event_valid_recordings=sum(int(r["eventValid"]) > 0 for r in rows),
                n_accepted_recordings=sum(int(r["accepted"]) > 0 for r in rows),
                **{
                    key: sum(int(r[key]) for r in rows)
                    for key in [
                        "trialRows",
                        "eventValid",
                        "intervalEligible",
                        "accepted",
                        "acceptedND",
                        "acceptedD",
                    ]
                },
            )
        )
    write("retention_by_session.csv", retention)
    counts = Counter((r["cohort"], r["rejection"]) for r in read("trial_quality.csv"))
    write(
        "rejection_counts.csv",
        [
            dict(cohort=c, reason=reason, n=n)
            for (c, reason), n in sorted(counts.items())
        ],
    )
    plot_results(participant, sessions, statuses)
    build_readme(cohort, participant, paired, statuses, retention)
    print("PARTICIPANT-WEIGHTED RESULTS:", flush=True)
    for r in cohort:
        print(
            r["cohort"],
            r["model_id"],
            f"BA={r['mean_balanced_accuracy']:.3f}, AUC={r['mean_mean_run_roc_auc']:.3f}, "
            f"participants={r['n_participants']}, sessions={r['n_sessions']}",
            flush=True,
        )


def plot_results(participant, sessions, statuses):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figdir = HERE / "figures"
    figdir.mkdir(exist_ok=True)
    lookup = {(r["subject"], r["model_id"]): r for r in participant}
    subjects = sorted(
        [
            r["subject"]
            for r in participant
            if r["cohort"] == "validation" and r["model_id"] == "LDA_full"
        ],
        key=lambda subject: lookup[subject, "LDA_full"]["balanced_accuracy"],
    )
    fig, axes = plt.subplots(
        1, 2, figsize=(12, 10), sharey=True, constrained_layout=True
    )
    for ax, metric, title in zip(
        axes,
        ["balanced_accuracy", "mean_run_roc_auc"],
        ["Balanced accuracy", "Mean held-out-run ROC-AUC"],
    ):
        for model, offset in zip(NAMES, [-0.18, 0, 0.18]):
            values = [lookup[s, model][metric] for s in subjects]
            ax.scatter(
                values,
                np.arange(len(subjects)) + offset,
                label=NAMES[model],
                color=COLORS[model],
                s=33,
            )
        ax.axvline(0.5, color=".5", linestyle="--", linewidth=0.8)
        ax.set_xlim(0.3, 1.01)
        ax.set_title(title)
        ax.grid(axis="x", alpha=0.2)
        ax.set_yticks(
            range(len(subjects)),
            [f"{s} ({lookup[s,'LDA_full']['n_sessions']} sessions)" for s in subjects],
        )
        ax.set_xlabel("Participant mean across eligible sessions")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="outside lower center", ncol=3)
    fig.suptitle(
        "Validation participants | Fixed 100 ms features | No FORCe | Matched whole-run holdouts"
    )
    fig.savefig(figdir / "validation_participant_scores.png", dpi=180)
    plt.close(fig)
    subjects = sorted(subjects)
    lookup = {(r["subject"], r["session"], r["model_id"]): r for r in sessions}
    fig, axes = plt.subplots(
        1, 3, figsize=(12, 10), sharey=True, constrained_layout=True
    )
    cmap = plt.colormaps["YlGnBu"].copy()
    cmap.set_bad("#dddddd")
    for ax, model in zip(axes, NAMES):
        values = np.array(
            [
                [
                    (
                        lookup[s, v, model]["balanced_accuracy"]
                        if (s, v, model) in lookup
                        else np.nan
                    )
                    for v in ["pre", "post", "retest"]
                ]
                for s in subjects
            ]
        )
        im = ax.imshow(values, cmap=cmap, vmin=0.3, vmax=1, aspect="auto")
        for i in range(len(subjects)):
            for j in range(3):
                label = f"{values[i,j]:.2f}" if np.isfinite(values[i, j]) else "—"
                ax.text(
                    j,
                    i,
                    label,
                    ha="center",
                    va="center",
                    fontsize=8,
                    color="white" if values[i, j] > 0.8 else "black",
                )
        ax.set_xticks(range(3), ["pre", "post", "retest"])
        ax.set_yticks(range(len(subjects)), subjects)
        ax.set_title(NAMES[model])
    fig.colorbar(
        im, ax=axes, shrink=0.8, label="Balanced accuracy; grey = not evaluable"
    )
    fig.suptitle(
        "Validation participants | Sessions kept separate | Same accepted trials and run holdouts"
    )
    fig.savefig(figdir / "validation_session_scores.png", dpi=180)
    plt.close(fig)


def build_readme(cohort, participant, paired, statuses, retention):
    validation = [r for r in cohort if r["cohort"] == "validation"]
    pilots = [r for r in cohort if r["cohort"] == "pilot"]
    paired_validation = [r for r in paired if r["cohort"] == "validation"]
    excluded = [r for r in statuses if r["status"] != "ok"]
    inventory = read("recording_inventory.csv")
    all_trials = sum(r["accepted"] for r in retention)
    evaluated_trials = sum(
        r["n_trials"] for r in participant if r["model_id"] == "LDA_full"
    )
    lines = [
        "# Fixed-decoder evaluation across the available dataset",
        "",
        "## Scope and protocol",
        "",
        "The available dataset contains 25 participants. The two decoder-selection pilots, "
        "mle01 and spe30, are reported separately. The remaining 23 participants assess the "
        "fixed configurations chosen during that pilot; this is internal validation, not an "
        "external cohort or a test of cross-participant model transfer. Each model is trained "
        "on other runs of the same participant and session.",
        "",
        "| Decoder | Channels | Features |",
        "|---|---|---:|",
        "| Shrinkage LDA | All eight | 56 |",
        "| Shrinkage LDA | Cz, FCz | 14 |",
        "| Binary decision tree | All eight | 56 |",
        "",
        "Each channel contributes seven non-overlapping 100 ms mean amplitudes over "
        "**[0.2, 0.9) s**. The montage is P3, PO3, PO7, CP5, CP1, Cz, FCz and FC1. "
        "All three decoders use identical accepted trial IDs and identical leave-one-complete-"
        "recording-out folds, separately for pre, post and retest. There is no hyperparameter "
        "search, feature ranking, threshold tuning or resampling.",
        "",
        'LDA uses training-fold StandardScaler, solver="lsqr", shrinkage="auto" and equal '
        "class priors [0.5,0.5]. The tree uses Gini impurity, best binary splits, unrestricted "
        "depth, minimum leaf size 1, no pruning, equal sample weights, and seed 20261027. "
        "These explicit tree defaults approximate the Graz classifier family; its precise "
        "hyperparameters were not reported. Class handling differs between the configured "
        "LDA and tree. This experiment does not reproduce the paper's 100 r-squared-selected "
        "features or 10-fold validation.",
        "",
        "## Preprocessing and data inclusion",
        "",
        "Filtering and final two-second epoch values are reused from saved PRE_01: "
        "continuous fourth-order 1–20 Hz Butterworth filtering with filtfilt, movement alignment, "
        "baseline correction over [−0.2,0) s, and rejection above 100 microvolts absolute "
        "amplitude across the complete two-second epoch and all eight channels. No FORCe or "
        "other reconstructive artifact removal is used. The exporter checks the stored settings.",
        "",
        "Raw loss codes, timestamp gaps and nonfinite EEG are checked over the complete "
        "[−1.5,1.5) s interval, with the same two-second valid-segment edge guards as the "
        "recent pilot. No labels or exclusions are revised after seeing classification results. "
        "All trials passing this no-FORCe pipeline are included; acceptance by any FORCe "
        "condition is irrelevant. The full signal and acceptance checks against the saved "
        "pilot controls are in `pilot_cache_verification.csv`.",
        "",
        f"There are {len(inventory)} inventoried recordings and {all_trials:,} accepted "
        f"trials. {evaluated_trials:,} accepted trials enter the evaluable sessions. "
        "Recordings with no valid events and trials that fail quality checks remain in the "
        "inventory and retention tables.",
        "",
        "A session needs at least two recording runs with accepted trials and both classes "
        "in every training fold. A single-class test fold still receives predictions; its "
        "run AUC and run BA are undefined. The session BA uses all its held-out predictions "
        "and both class totals. AUC averages only defined, two-class held-out-run AUCs; "
        "their number is recorded.",
        "",
        "Original labels: 1 = non-displaced (binary 0), 2 = displaced (binary 1). "
        "Sensitivity concerns displaced trials; specificity concerns non-displaced trials.",
        "",
        "## Primary validation results",
        "",
        "**Participant weighting:** first average each metric across eligible sessions "
        "within a participant, then average participants equally. The table is not weighted "
        "by trial counts. Session BA comes from pooled out-of-fold class recalls; session "
        "AUC is the mean of defined held-out-run AUCs.",
        "",
        "| Decoder | Participants | Sessions | Accuracy | BA | D sensitivity | ND specificity | AUC |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for r in validation:
        lines.append(
            f"| {r['model']} | {r['n_participants']} | {r['n_sessions']} | "
            + " | ".join(
                f"{r['mean_'+key]:.3f}"
                for key in [
                    "accuracy",
                    "balanced_accuracy",
                    "sensitivity_D",
                    "specificity_ND",
                    "mean_run_roc_auc",
                ]
            )
            + " |"
        )
    full = next(r for r in validation if r["model_id"] == "LDA_full")
    central = next(r for r in validation if r["model_id"] == "LDA_central")
    wins = sum(r["delta_BA_full_minus_central"] > 1e-12 for r in paired_validation)
    ties = sum(
        abs(r["delta_BA_full_minus_central"]) <= 1e-12 for r in paired_validation
    )
    lines += [
        "",
        f"Full-montage LDA has higher participant-mean BA in {wins}/{len(paired_validation)} "
        f"validation participants ({ties} ties). Its participant-weighted mean difference "
        f"from Central is {100*(full['mean_balanced_accuracy']-central['mean_balanced_accuracy']):+.2f} "
        "percentage points. This is a descriptive paired comparison, not a population significance test.",
        "",
        "## Pilot results, kept separate",
        "",
        "| Decoder | Participants | Sessions | Accuracy | BA | AUC |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for r in pilots:
        lines.append(
            f"| {r['model']} | {r['n_participants']} | {r['n_sessions']} | {r['mean_accuracy']:.3f} | "
            f"{r['mean_balanced_accuracy']:.3f} | {r['mean_mean_run_roc_auc']:.3f} |"
        )
    lines += [
        "",
        "These pilot models are refitted on all accepted no-FORCe trials. Their scores "
        "can differ from the earlier four-condition matched pilot because the acceptance "
        "intersection and training trial counts have changed.",
        "",
        "## Sessions excluded from cross-validation",
        "",
        "| Participant / session | Accepted trials | Accepted recordings | Reason |",
        "|---|---:|---:|---|",
    ]
    for r in excluded:
        lines.append(
            f"| {r['subject']} / {r['session']} | {r['n_accepted']} | {r['n_accepted_recordings']} | {r['status']} |"
        )
    if not excluded:
        lines.append("| None | — | — | — |")
    lines += [
        "",
        "## Interpretation limits",
        "",
        "- This evaluates personalised decoders on held-out recording runs. Models do "
        "not transfer from other participants or sessions. Validation participants were "
        "outside this two-participant decoder-selection pilot; previous exploratory work "
        "on the dataset means this should not be described as a blinded external test.",
        "- A full-montage advantage does not localise the source of predictive information. "
        "The additional channels include FC1 as well as centroparietal/posterior electrodes.",
        "- Better prediction does not establish that the signal is specifically a neural "
        "ErrP or that accepted epochs are artifact-free. The no-FORCe acceptance rules "
        "remain the existing quality-control baseline.",
        "- The unpruned tree may give pure-leaf probabilities of 0/1, so its within-run "
        "AUC can equal BA. LDA and tree score ranges and class handling differ. No settings "
        "are changed in response to these results.",
        "- Participants with an excluded session are averaged over their remaining "
        "eligible sessions; session-level results and retention counts expose this coverage.",
        "",
        "## Outputs and reproduction",
        "",
        "- `cohort_summary.csv`: equal-participant validation and separate pilot summaries.",
        "- `participant_metrics.csv`, `session_metrics.csv`, `fold_metrics.csv`: all evaluation levels.",
        "- `heldout_predictions.csv`: individual test predictions, original trial IDs and scores.",
        "- `paired_participant_differences.csv`: paired decoder differences.",
        "- `trial_quality.csv`, `retention_by_run.csv`, `retention_by_session.csv`, "
        "`rejection_counts.csv`: complete inclusion and rejection accounting.",
        "- `session_eligibility.csv`: why any session cannot support the fixed evaluation.",
        "- `analysis_settings.json`: exact frozen model and preprocessing settings.",
        "- `figures/validation_participant_scores.png`: participant-wise BA and AUC.",
        "- `figures/validation_session_scores.png`: separate session results for all models.",
        "",
        "[Methods, settings and execution order](../../../Code/analyses/DEC_decoding/README.md#dec_02).",
        "",
        "Reference: [Graz paper](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf).",
        "",
    ]
    if (result_path("DEC_03") / "README.md").exists():
        lines += [
            "## Graz-style tree feature comparison",
            "",
            "The [matched decision-tree feature comparison](../DEC_03_graz_comparison/README.md) "
            "adds 100 training-fold r-squared-selected channel/time amplitudes from the "
            "full epoch, a same-interval 0.2–0.9 s control, and trees using the four "
            "audited channel sets. It preserves the results above and documents the "
            "paper's unspecified classifier interval and tree settings.",
            "",
        ]
    if (
        ROOT / "output/DEC_decoding/report/D_ND_classification_research_note.pdf"
    ).exists():
        lines += [
            "## Research note",
            "",
            "The consolidated [D/ND classification research note](../report/D_ND_classification_research_note.pdf) "
            "covers the matched pilot, fixed full-dataset evaluation and Graz-style tree "
            "feature comparison. Its editable LaTeX project is in `../report/`.",
            "",
        ]
    (HERE / "README.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    # CSV numbers are strings on disk; the summariser expects numeric metrics.
    def numeric_rows(name):
        rows = read(name)
        for row in rows:
            for key, value in row.items():
                try:
                    row[key] = float(value)
                except (ValueError, TypeError):
                    pass
        return rows

    summarise(
        numeric_rows("session_metrics.csv"),
        numeric_rows("fold_metrics.csv"),
        numeric_rows("session_eligibility.csv"),
    )
