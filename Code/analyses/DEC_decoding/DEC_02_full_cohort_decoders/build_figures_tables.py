"""Build note tables/figures from saved classification results; no model refits."""

# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = ROOT / "output/DEC_decoding/report"
OUTPUT = HERE.parent
FULL = result_path("DEC_02")
PILOT = result_path("DEC_01") / "channel_sets"
GRAZ = result_path("DEC_03")
FIG = HERE / "figures"
TAB = HERE / "tables"
FIG.mkdir(exist_ok=True)
TAB.mkdir(exist_ok=True)
plt.rcParams.update(
    {
        "font.size": 8.5,
        "axes.titlesize": 9,
        "axes.labelsize": 8.5,
        "legend.fontsize": 8,
        "pdf.fonttype": 42,
        "savefig.dpi": 200,
    }
)


def read(path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def pct(value):
    return f"{100*float(value):.1f}"


def tabular(name, headers, rows, alignment):
    text = [
        r"\begin{tabular}{@{}" + alignment + r"@{}}",
        r"\toprule",
        " & ".join(headers) + r" \\",
        r"\midrule",
    ]
    text += [" & ".join(str(x) for x in row) + r" \\" for row in rows]
    text += [r"\bottomrule", r"\end{tabular}"]
    (TAB / name).write_text("\n".join(text) + "\n", encoding="utf-8")


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", bbox_inches="tight")
    plt.close(fig)


cohort = read(FULL / "cohort_summary.csv")
participants = read(FULL / "participant_metrics.csv")
sessions = read(FULL / "session_metrics.csv")
graz_cohort = read(GRAZ / "cohort_summary.csv")
graz_participants = read(GRAZ / "participant_metrics.csv")
pilot = read(PILOT / "descriptive_pilot_summary.csv")
pilot_sessions = read(PILOT / "session_metrics.csv")
models = ["LDA_full", "LDA_central", "DT_full"]
labels = {
    "LDA_full": "LDA, all eight",
    "LDA_central": "LDA, Cz/FCz",
    "DT_full": "Tree, all eight",
}
colors = {"LDA_full": "#1b5e91", "LDA_central": "#36998d", "DT_full": "#b46222"}

for split, filename in [
    ("validation", "cohort_main.tex"),
    ("pilot", "pilot_refit.tex"),
]:
    rows = []
    for model in models:
        r = next(r for r in cohort if (r["cohort"], r["model_id"]) == (split, model))
        rows.append(
            [
                labels[model],
                pct(r["mean_accuracy"]),
                pct(r["mean_balanced_accuracy"]),
                pct(r["mean_sensitivity_D"]),
                pct(r["mean_specificity_ND"]),
                f"{float(r['mean_mean_run_roc_auc']):.3f}",
            ]
        )
    tabular(
        filename,
        ["Decoder", "Acc.", "BA", "D recall", "ND recall", "AUC"],
        rows,
        "lrrrrr",
    )

rows = []
for name in ["Central", "Centroparietal", "Posterior", "Full"]:
    scores = []
    for rep in ["100ms", "50ms", "samples"]:
        r = next(
            r
            for r in pilot
            if (r["condition_id"], r["channel_set"], r["representation"])
            == ("1", name, rep)
        )
        scores.append(pct(r["mean_session_balanced_accuracy"]))
    rows.append([name] + scores)
tabular(
    "pilot_resolution.tex", ["Channel set", "100 ms", "50 ms", "Samples"], rows, "lrrr"
)

rows = []
condition_names = {
    1: "BP, no FORCe",
    2: "BP, FORCe",
    3: "Split, no FORCe",
    4: "Split, FORCe",
}
for cid in range(1, 5):
    scores = []
    for name in ["Central", "Centroparietal", "Posterior", "Full"]:
        r = next(
            r
            for r in pilot
            if (r["condition_id"], r["channel_set"], r["representation"])
            == (str(cid), name, "100ms")
        )
        scores.append(pct(r["mean_session_balanced_accuracy"]))
    rows.append([str(cid), condition_names[cid]] + scores)
tabular(
    "pilot_processing.tex",
    ["ID", "Processing", "Central", "Centroparietal", "Posterior", "Full"],
    rows,
    "llrrrr",
)

rows = []
graz_labels = {
    "DT_r2_epoch": r"Top 100 $r^2$, $[-1,1)$ s",
    "DT_r2_response": r"Top 100 $r^2$, $[0.2,0.9)$ s",
    "DT_Central": "100 ms, Central",
    "DT_Centroparietal": "100 ms, Centroparietal",
    "DT_Posterior": "100 ms, Posterior",
    "DT_Full": "100 ms, Full",
}
counts = [100, 100, 14, 14, 21, 56]
for model, n_features in zip(graz_labels, counts):
    r = next(
        r for r in graz_cohort if (r["cohort"], r["model_id"]) == ("validation", model)
    )
    rows.append(
        [
            graz_labels[model],
            str(n_features),
            pct(r["mean_accuracy"]),
            pct(r["mean_balanced_accuracy"]),
            pct(r["mean_sensitivity_D"]),
            pct(r["mean_specificity_ND"]),
            f"{float(r['mean_mean_run_roc_auc']):.3f}",
        ]
    )
tabular(
    "graz_results.tex",
    ["Feature design", "$p$", "Acc.", "BA", "D recall", "ND recall", "AUC"],
    rows,
    "lrrrrrr",
)

status = read(FULL / "session_eligibility.csv")
retention = read(FULL / "retention_by_session.csv")
rows = []
for split, label in [("validation", "Validation"), ("pilot", "Pilots")]:
    r = [r for r in retention if r["cohort"] == split]
    c = next(r for r in cohort if (r["cohort"], r["model_id"]) == (split, "LDA_full"))
    eval_sessions = [
        s for s in sessions if (s["cohort"], s["model_id"]) == (split, "LDA_full")
    ]
    rows.append(
        [
            label,
            c["n_participants"],
            sum(int(x["eventValid"]) for x in r),
            sum(int(x["accepted"]) for x in r),
            c["n_trials"],
            sum(int(x["n_ND"]) for x in eval_sessions),
            sum(int(x["n_D"]) for x in eval_sessions),
            c["n_sessions"],
        ]
    )
tabular(
    "retention.tex",
    ["Cohort", "$N$", "Event-valid", "Accepted", "Evaluated", "ND", "D", "Sessions"],
    rows,
    "lrrrrrrr",
)

lookup = {(r["subject"], r["model_id"]): r for r in participants}
glookup = {(r["subject"], r["model_id"]): r for r in graz_participants}
subjects = sorted({r["subject"] for r in participants if r["cohort"] == "validation"})
rows = []
for s in subjects:
    r = lookup[s, "LDA_full"]
    rows.append(
        [s, r["n_sessions"], r["n_trials"]]
        + [pct(lookup[s, m]["balanced_accuracy"]) for m in models]
        + [
            pct(glookup[s, m]["balanced_accuracy"])
            for m in ["DT_r2_epoch", "DT_r2_response"]
        ]
    )
tabular(
    "participant_results.tex",
    [
        "Participant",
        "Sessions",
        "Trials",
        "LDA8",
        "LDA2",
        "Tree8",
        r"$r^2$ full",
        r"$r^2$ resp.",
    ],
    rows,
    "lrrrrrrr",
)

rows = []
for s in ["mle01", "spe30"]:
    for session in ["pre", "post", "retest"]:
        values = []
        for cid in range(1, 5):
            r = next(
                r
                for r in pilot_sessions
                if (
                    r["subject"],
                    r["session"],
                    r["condition_id"],
                    r["channel_set"],
                    r["representation"],
                )
                == (s, session, str(cid), "Full", "100ms")
            )
            values.append(pct(r["balanced_accuracy"]))
        rows.append([s, session] + values)
tabular(
    "pilot_sessions.tex",
    [
        "Participant",
        "Session",
        "Condition 1",
        "Condition 2",
        "Condition 3",
        "Condition 4",
    ],
    rows,
    "llrrrr",
)

# Compact, vector figures sized for the manuscript's text width.
fig, axes = plt.subplots(1, 2, figsize=(7, 6.1), sharey=True, constrained_layout=True)
order = sorted(subjects, reverse=True)
for ax, metric, title in zip(
    axes,
    ["balanced_accuracy", "mean_run_roc_auc"],
    ["Balanced accuracy", "Mean run ROC-AUC"],
):
    for model, offset in zip(models, [-0.18, 0, 0.18]):
        ax.scatter(
            [float(lookup[s, model][metric]) for s in order],
            np.arange(len(order)) + offset,
            label=labels[model],
            color=colors[model],
            s=16,
        )
    ax.axvline(0.5, color=".5", linestyle=":", linewidth=0.8)
    ax.set_xlim(0.35, 1)
    ax.set_title(title)
    ax.grid(axis="x", alpha=0.2)
    ax.set_xticks([0.4, 0.6, 0.8, 1])
    ax.set_yticks(
        range(len(order)),
        [
            s + ("*" if lookup[s, "LDA_full"]["n_sessions"] == "2" else "")
            for s in order
        ],
    )
    ax.set_xlabel("Participant mean")
handles, legend = axes[0].get_legend_handles_labels()
fig.legend(handles, legend, loc="outside lower center", ncol=3)
save(fig, "participant_scores")

slookup = {(r["subject"], r["session"], r["model_id"]): r for r in sessions}
fig, axes = plt.subplots(1, 3, figsize=(7, 6.4), sharey=True, constrained_layout=True)
cmap = plt.colormaps["YlGnBu"].copy()
cmap.set_bad("#dddddd")
for ax, model in zip(axes, models):
    values = np.array(
        [
            [
                (
                    float(slookup[s, v, model]["balanced_accuracy"])
                    if (s, v, model) in slookup
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
            text = f"{values[i,j]:.2f}" if np.isfinite(values[i, j]) else "--"
            ax.text(
                j,
                i,
                text,
                ha="center",
                va="center",
                fontsize=7.7,
                color="white" if values[i, j] > 0.8 else "black",
            )
    ax.set_xticks(range(3), ["pre", "post", "retest"])
    ax.set_yticks(range(len(subjects)), subjects)
    ax.set_title(labels[model])
fig.colorbar(im, ax=axes, shrink=0.75, label="Balanced accuracy")
save(fig, "session_scores")

fig, axes = plt.subplots(2, 1, figsize=(7, 5.3), sharex=True, constrained_layout=True)
gmodels = list(graz_labels)
for ax, metric, title in zip(
    axes,
    ["balanced_accuracy", "mean_run_roc_auc"],
    ["Balanced accuracy", "Mean run ROC-AUC"],
):
    values = np.array(
        [[float(glookup[s, m][metric]) for m in gmodels] for s in subjects]
    )
    for row in values:
        ax.plot(
            range(6), row, "o-", color=".5", alpha=0.28, markersize=2, linewidth=0.5
        )
    ax.plot(
        range(6),
        values.mean(axis=0),
        "D-",
        color="#1b5e91",
        markersize=4,
        linewidth=1.5,
        label="Participant-weighted tree mean",
    )
    ref = next(
        r for r in cohort if (r["cohort"], r["model_id"]) == ("validation", "LDA_full")
    )
    ax.axhline(
        float(ref["mean_" + metric]),
        color="#36998d",
        linestyle="--",
        label="Full LDA mean",
    )
    ax.axhline(0.5, color=".4", linestyle=":", linewidth=0.7)
    ax.set_ylim(0.35, 1)
    ax.set_ylabel(title)
    ax.grid(axis="y", alpha=0.2)
    ax.set_xticks(
        range(6),
        [
            "$r^2$100\nFull epoch",
            "$r^2$100\nResponse",
            "Central\nbins",
            "Centroparietal\nbins",
            "Posterior\nbins",
            "Full\nbins",
        ],
        fontsize=7.5,
    )
handles, legend = axes[0].get_legend_handles_labels()
fig.legend(handles, legend, loc="outside lower center", ncol=2)
save(fig, "graz_comparison")
print("Generated eight result tables and three vector figures from saved metrics.")
