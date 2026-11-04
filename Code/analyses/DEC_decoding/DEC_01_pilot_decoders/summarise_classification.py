"""Plot and summarise the saved held-out predictions; no model refitting."""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv
import json
from collections import defaultdict
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = ROOT / "output/DEC_decoding/DEC_01_pilot_decoders"
FIG = HERE / "figures"
FIG.mkdir(exist_ok=True)
CONDITIONS = {1: "BP no-FORCe", 2: "BP FORCe", 3: "Split no-FORCe", 4: "Split FORCe"}
COLORS = {1: "#1b5e91", 2: "#d27912", 3: "#36998d", 4: "#a14375"}
REPS = ["100ms", "50ms", "samples"]
LABELS = ["100 ms\n14 features", "50 ms\n28 features", "Samples\n700 features"]
GROUPS = [(s, v) for s in ["mle01", "spe30"] for v in ["pre", "post", "retest"]]
plt.rcParams.update(
    {
        "font.size": 10,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "pdf.fonttype": 42,
        "savefig.dpi": 180,
    }
)


def read(name):
    with (HERE / name).open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (HERE / name).open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def save(fig, name):
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    plt.close(fig)


def main():
    rows, folds = read("session_metrics.csv"), read("fold_metrics.csv")
    lookup = {
        (r["subject"], r["session"], int(r["condition_id"]), r["representation"]): r
        for r in rows
    }
    # Heatmaps use primary metrics: pooled OOF confusion counts for BA; within-run AUC then mean.
    fig, axes = plt.subplots(2, 1, figsize=(15, 8), constrained_layout=True)
    columns = [(c, r) for c in CONDITIONS for r in REPS]
    for ax, metric, title in zip(
        axes,
        ["balanced_accuracy", "mean_run_roc_auc"],
        [
            "Balanced accuracy from all held-out predictions",
            "Mean held-out-run ROC-AUC",
        ],
    ):
        values = np.array(
            [[float(lookup[s, v, c, r][metric]) for c, r in columns] for s, v in GROUPS]
        )
        im = ax.imshow(values, vmin=0.5, vmax=1, cmap="YlGnBu", aspect="auto")
        ax.set_yticks(range(6), [f"{s} / {v}" for s, v in GROUPS])
        ax.set_xticks(
            range(12),
            [
                f'{CONDITIONS[c]}\n{r if r != "samples" else "Samples"}'
                for c, r in columns
            ],
            fontsize=8,
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
                    color="white" if values[i, j] > 0.82 else "black",
                    fontsize=9,
                )
        for x in [2.5, 5.5, 8.5]:
            ax.axvline(x, color="white", linewidth=3)
        ax.axhline(2.5, color="white", linewidth=3)
        fig.colorbar(im, ax=ax, shrink=0.85, label="Score; chance reference = 0.5")
    fig.suptitle(
        "Displaced vs non-displaced | Cz + FCz, 0.2–0.9 s | Matched trials, whole-run holdouts",
        fontsize=14,
    )
    save(fig, "classification_scores")
    # Show run variability rather than treating correlated CV folds as independent confidence intervals.
    fig, axes = plt.subplots(
        2, 3, figsize=(13, 7), sharex=True, sharey=True, constrained_layout=True
    )
    offsets = {1: -0.12, 2: -0.04, 3: 0.04, 4: 0.12}
    for ax, (subject, session) in zip(axes.ravel(), GROUPS):
        for cid in CONDITIONS:
            means = []
            for j, rep in enumerate(REPS):
                selected = [
                    r
                    for r in folds
                    if (
                        r["subject"],
                        r["session"],
                        int(r["condition_id"]),
                        r["representation"],
                    )
                    == (subject, session, cid, rep)
                ]
                values = [float(r["balanced_accuracy"]) for r in selected]
                x = j + offsets[cid]
                ax.scatter(
                    np.full(len(values), x), values, s=17, color=COLORS[cid], alpha=0.4
                )
                means.append(np.mean(values))
            ax.plot(
                np.arange(3) + offsets[cid],
                means,
                "-o",
                color=COLORS[cid],
                linewidth=1.6,
                markersize=5,
            )
        ax.axhline(0.5, linestyle="--", color=".4", linewidth=0.8)
        ax.set_title(f"{subject} / {session}")
        ax.set_xticks(range(3), LABELS, fontsize=9)
        ax.set_ylim(0.2, 1.01)
        ax.grid(axis="y", alpha=0.2)
    for ax in axes[:, 0]:
        ax.set_ylabel("Held-out-run balanced accuracy")
    handles = [
        Line2D([0], [0], color=COLORS[c], marker="o", label=CONDITIONS[c])
        for c in CONDITIONS
    ]
    fig.legend(handles=handles, loc="outside lower center", ncol=4)
    fig.suptitle(
        "Run variability: faint dots = individual held-out runs; connected points = mean across runs",
        fontsize=12,
    )
    save(fig, "heldout_run_variability")
    # Secondary class-specific metrics help reveal gains driven mainly by one class.
    fig, axes = plt.subplots(
        2, 3, figsize=(13, 7), sharex=True, sharey=True, constrained_layout=True
    )
    for ax, (subject, session) in zip(axes.ravel(), GROUPS):
        for cid in CONDITIONS:
            for metric, style, marker in [
                ("sensitivity_D", "-", "o"),
                ("specificity_ND", "--", "s"),
            ]:
                values = [
                    float(lookup[subject, session, cid, rep][metric]) for rep in REPS
                ]
                ax.plot(
                    range(3),
                    values,
                    style,
                    marker=marker,
                    color=COLORS[cid],
                    markersize=4,
                )
        ax.set_title(f"{subject} / {session}")
        ax.set_xticks(range(3), LABELS, fontsize=9)
        ax.set_ylim(0.25, 1.01)
        ax.grid(axis="y", alpha=0.2)
    for ax in axes[:, 0]:
        ax.set_ylabel("Class recall")
    fig.legend(handles=handles, loc="outside lower center", ncol=4)
    fig.suptitle(
        "Class recall: solid = displaced sensitivity; dashed = non-displaced specificity",
        fontsize=12,
    )
    save(fig, "class_specific_scores")
    aggregate = []
    for cid in CONDITIONS:
        for rep in REPS:
            selected = [
                r
                for r in rows
                if int(r["condition_id"]) == cid and r["representation"] == rep
            ]
            aggregate.append(
                dict(
                    condition_id=cid,
                    condition=CONDITIONS[cid],
                    representation=rep,
                    n_participant_sessions=6,
                    mean_session_balanced_accuracy=float(
                        np.mean([float(r["balanced_accuracy"]) for r in selected])
                    ),
                    mean_session_run_roc_auc=float(
                        np.mean([float(r["mean_run_roc_auc"]) for r in selected])
                    ),
                    mean_session_sensitivity_D=float(
                        np.mean([float(r["sensitivity_D"]) for r in selected])
                    ),
                    mean_session_specificity_ND=float(
                        np.mean([float(r["specificity_ND"]) for r in selected])
                    ),
                )
            )
    write("descriptive_pilot_summary.csv", aggregate)
    contrasts = read("paired_fold_differences.csv")
    contrast_groups = defaultdict(list)
    for r in contrasts:
        key = tuple(
            r[k]
            for k in [
                "subject",
                "session",
                "comparison",
                "condition_a",
                "representation_a",
                "condition_b",
                "representation_b",
            ]
        )
        contrast_groups[key].append(r)
    contrast_summary = []
    for key, values in contrast_groups.items():
        r = dict(
            zip(
                [
                    "subject",
                    "session",
                    "comparison",
                    "condition_a",
                    "representation_a",
                    "condition_b",
                    "representation_b",
                ],
                key,
            )
        )
        r["n_runs"] = len(values)
        for metric in [
            "balanced_accuracy",
            "roc_auc",
            "sensitivity_D",
            "specificity_ND",
        ]:
            delta = np.array([float(v[f"delta_{metric}"]) for v in values])
            r[f"mean_delta_{metric}"] = float(np.mean(delta))
            if metric == "balanced_accuracy":
                r["runs_higher_BA"] = int(np.sum(delta > 1e-12))
                r["runs_equal_BA"] = int(np.sum(np.abs(delta) <= 1e-12))
                r["runs_lower_BA"] = int(np.sum(delta < -1e-12))
        contrast_summary.append(r)
    write("paired_comparison_summary.csv", contrast_summary)
    text = []
    text += [
        "# Displaced versus non-displaced classification pilot",
        "",
        "## What was tested",
        "",
        "Fixed shrinkage LDA using Cz and FCz over **[0.2, 0.9) s**, separately for each participant and session. "
        "The three representations are seven 100 ms means/channel (14 features), fourteen 50 ms means/channel "
        "(28 features), and all 350 original 500 Hz samples/channel (700 features). Every representation "
        "uses the same interval. No samples were downsampled for the original-sample representation.",
        "",
        "| ID | Processing condition |",
        "|---|---|",
    ]
    for cid, name in CONDITIONS.items():
        text.append(f"| {cid} | {name} |")
    text += [
        "",
        "Conditions 1/2 use continuous 1–20 Hz bandpass filtering; 2 then applies FORCe to three "
        "one-second windows. Conditions 3/4 use continuous 1 Hz high-pass filtering followed by a 20 Hz "
        "low-pass on the three-second segment; 4 applies FORCe to three one-second windows before that "
        "low-pass. All use the saved, cropped two-second epochs, identical baseline correction, and "
        "FORCe window boundaries at −0.5 and +0.5 s in conditions 2/4. The feature interval therefore includes the +0.5 s "
        "boundary. This test uses these saved conditions; it does not test the historical two-window join at onset.",
        "",
        "## Validation and trial matching",
        "",
        "- 2,562 trial IDs accepted in all four conditions; no new input-flag exclusions. Original label 1 "
        "means non-displaced (ND); label 2 means displaced (D). D is the positive classification class.",
        "- Each participant/session is analysed independently. Leave one complete recording run out; "
        "the other runs train the model. No run is shared by training and test sets.",
        "- Five folds per participant/session, except spe30/retest: four available runs (1, 3, 4, 5). "
        "All configurations use identical held-out trial IDs.",
        '- Model: training-fold StandardScaler, then LDA with solver="lsqr", shrinkage="auto" and '
        "equal class priors [0.5, 0.5]. No tuning, feature selection, threshold search or resampling. "
        "Shrinkage is estimated using training data only. Decision score > 0 predicts D.",
        "- 348 fitted models; 30,744 predictions. Every trial receives exactly one held-out prediction "
        "per condition/representation.",
        "",
        "This tests generalisation to another run **within the same participant/session**, not to an "
        "unseen session or participant. The pilot data have already informed the channel and interval "
        "choices; these are exploratory results.",
        "",
        "## Metrics",
        "",
        "**Balanced accuracy (BA)** = (D sensitivity + ND specificity)/2, computed from the pooled "
        "out-of-fold confusion counts within each participant/session. **Primary ROC-AUC** is the "
        "unweighted mean of the held-out-run AUCs: separate fitted folds may have different score scales. "
        "The pooled OOF AUC is also saved as a secondary metric. A constant majority classifier has BA "
        "and AUC 0.5. This is a chance reference, not a significance threshold.",
        "",
        "The run-variability figure shows each held-out-run BA and its arithmetic mean, which can differ "
        "from pooled OOF BA when run/class counts differ. Ranges across runs are descriptive, not "
        "confidence intervals. No population significance tests are made.",
        "",
        "## Primary no-FORCe results",
        "",
        "Each cell below is **BA / mean-run AUC** for condition 1.",
        "",
        "| Participant / session | ND / D | Runs | 100 ms | 50 ms | Samples |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for subject, session in GROUPS:
        first = lookup[subject, session, 1, "100ms"]
        cells = [
            f"{float(lookup[subject,session,1,rep]['balanced_accuracy']):.3f} / {float(lookup[subject,session,1,rep]['mean_run_roc_auc']):.3f}"
            for rep in REPS
        ]
        text.append(
            f"| {subject} / {session} | {first['n_ND']} / {first['n_D']} | {first['n_runs']} | "
            + " | ".join(cells)
            + " |"
        )
    text += [
        "",
        "## Comparison of all conditions",
        "",
        "Below are unweighted descriptive means across the six participant/session results. "
        "They are not six independent participants or an estimate of population performance.",
        "",
        "| Condition | Representation | Mean BA | Mean run-AUC | D sensitivity | ND specificity |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for r in aggregate:
        text.append(
            f"| {r['condition']} | {r['representation']} | {r['mean_session_balanced_accuracy']:.3f} | "
            f"{r['mean_session_run_roc_auc']:.3f} | {r['mean_session_sensitivity_D']:.3f} | {r['mean_session_specificity_ND']:.3f} |"
        )
    force_delta = np.array(
        [
            float(lookup[s, v, 2, r]["balanced_accuracy"])
            - float(lookup[s, v, 1, r]["balanced_accuracy"])
            for s, v in GROUPS
            for r in REPS
        ]
    )
    split_delta = np.array(
        [
            float(lookup[s, v, 4, r]["balanced_accuracy"])
            - float(lookup[s, v, 3, r]["balanced_accuracy"])
            for s, v in GROUPS
            for r in REPS
        ]
    )
    filter_delta = np.array(
        [
            float(lookup[s, v, 3, r]["balanced_accuracy"])
            - float(lookup[s, v, 1, r]["balanced_accuracy"])
            for s, v in GROUPS
            for r in REPS
        ]
    )
    text += [
        "",
        "## Interpretation",
        "",
        "- **100 ms bins remain a sensible first baseline.** In the primary condition, they give the "
        "highest BA in four of six participant/sessions; original samples give the highest BA in two. "
        "50 ms bins have no consistent advantage. The six-session mean BA favours 100 ms, with far fewer "
        "features than the original samples. This supports a practical starting point, not a universal "
        "optimal bin width.",
        f"- **The two no-FORCe controls are similar:** the largest absolute BA difference between "
        f"conditions 3 and 1 is {100 * np.max(np.abs(filter_delta)):.2f} percentage points across the "
        "18 participant/session/representation comparisons.",
        f"- **FORCe does not improve classification consistently:** BP FORCe has lower BA than its "
        f"matched BP control in {np.sum(force_delta < 0)}/18 comparisons; split FORCe has lower BA "
        f"than its split control in {np.sum(split_delta < 0)}/18. These are descriptive comparisons "
        "of related results, not independent statistical tests.",
        "- **Session differences remain:** spe30/retest is weaker than spe30/pre and post. The "
        "held-out-run figure shows substantial run variability, so a single pooled pilot score would "
        "hide useful differences.",
        "- These findings support continuing with no-FORCe as the primary working analysis and "
        "100 ms Cz/FCz features as a compact baseline, while retaining 50 ms and original-sample "
        "results as sensitivities. They do not establish that FORCe removes useful neural activity: "
        "better prediction can also exploit contamination or other class-related differences. "
        "Likewise, predictive class information alone does not identify a neural ErrP component.",
        "- The next independent question would be how this fixed baseline transfers to other "
        "sessions or participants. That was not tested here.",
        "",
        "## Files and reproduction",
        "",
        "- `export_central_features.m`: extracts matched Cz/FCz data from saved epochs; verifies the "
        "100 ms features against the prior feature audit.",
        "- `analyse_classification.py`: fits the fixed models and verifies matching and OOF coverage.",
        "- `summarise_classification.py`: builds this summary and the plots from saved scores.",
        "- `trial_metadata.csv`: original recording/run/trial IDs and labels.",
        "- `session_metrics.csv`: all 72 participant/session/configuration summaries and confusion counts.",
        "- `fold_metrics.csv`: all 348 held-out-run scores and training/test class counts.",
        "- `heldout_predictions.csv`: 30,744 individual held-out predictions and decision scores.",
        "- `paired_fold_differences.csv` and `paired_comparison_summary.csv`: identical-fold comparisons "
        "for FORCe, filtering, and temporal representation.",
        "- `descriptive_pilot_summary.csv`: six-session descriptive means.",
        "- `analysis_settings.json` and `requirements.txt`: model settings, checks and package versions.",
        "- `figures/classification_scores.png`: all session scores; `heldout_run_variability.png`: "
        "individual folds; `class_specific_scores.png`: class-specific recalls. Vector PDF copies "
        "are also saved for reuse in a later research note.",
        "",
        "From the repository root, run the export with MATLAB, then run the two Python scripts in "
        "the recorded environment. The local `.venv`, exported MAT data and temporary files are ignored. "
        "Existing pipeline outputs and earlier research notes are preserved.",
        "",
        "Method references: [scikit-learn LDA](https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html), "
        "[leave-one-group-out](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html).",
        "",
    ]
    if (HERE / "decision_tree" / "README.md").exists():
        text += [
            "## Decision-tree follow-up",
            "",
            "The [Graz-style decision-tree comparison](decision_tree/README.md) applies the "
            "same 14 binned Cz/FCz features to the primary no-FORCe data, using identical "
            "whole-run holdouts. It preserves the LDA results above and documents assumptions "
            "needed because the paper omits the tree hyperparameters. Run "
            "`analyse_decision_tree.py` after this analysis.",
            "",
        ]
    if (HERE / "channel_sets" / "README.md").exists():
        text += [
            "## All audited channel sets",
            "",
            "The [expanded LDA comparison](channel_sets/README.md) uses Central, "
            "Centroparietal, Posterior and Full channel sets, with the same three temporal "
            "representations, four processing conditions and held-out runs. Run the extended "
            "`export_central_features.m`, then `analyse_channel_sets.py`. Original Central "
            "results are reused; the other three groups use the same shared LDA settings.",
            "",
        ]
    (HERE / "README.md").write_text("\n".join(text), encoding="utf-8")
    print(json.dumps(aggregate, indent=2))
    print(
        "SUMMARY COMPLETE: three figures, descriptive and paired comparison tables, README."
    )


if __name__ == "__main__":
    main()
