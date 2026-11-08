"""Prepare compact LDA-note inputs from completed DEC_04 permutation results."""

from pathlib import Path
import sys, csv

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def main():
    with (result_path("DEC_04") / "participant_significance.csv").open(
        newline="", encoding="utf-8-sig"
    ) as f:
        rows = list(csv.DictReader(f))
    primary = [
        r for r in rows if r["model_id"] == "LDA_full" and r["cohort"] == "validation"
    ]
    pilots = [r for r in rows if r["model_id"] == "LDA_full" and r["cohort"] == "pilot"]
    assert len(primary) == 23 and len(pilots) == 2
    report = ROOT / "output/DEC_decoding/report"
    tables = report / "tables"
    figures = report / "figures"
    for folder in [tables, figures]:
        folder.mkdir(exist_ok=True)
    for name, data in [
        ("permutation_primary", primary),
        ("permutation_pilots", pilots),
    ]:
        lines = [
            r"\begin{tabular}{@{}lrrrrrr@{}}\toprule",
            r"Participant & Sessions & Trials & BA (\%) & Chance$_{95}$ (\%) & $p$ & $p_{\mathrm{Holm}}$\\\midrule",
        ]
        for r in data:
            p = float(r["p_value"])
            adj = float(r["p_holm"])
            lines.append(
                f"{r['subject']} & {r['n_sessions']} & {int(r['n_trials']):,} & {100*float(r['balanced_accuracy']):.1f} & {100*float(r['chance_95']):.1f} & {p:.4f} & {adj:.4f}"
                + r"\\"
            )
        lines += [r"\bottomrule\end{tabular}"]
        (tables / (name + ".tex")).write_text("\n".join(lines) + "\n")
    n_sig = sum(float(r["p_holm"]) <= 0.05 for r in primary)
    lo = min(100 * float(r["chance_95"]) for r in primary)
    hi = max(100 * float(r["chance_95"]) for r in primary)
    text = (
        f"Eight-channel shrinkage LDA exceeded the within-recording label-shuffle null after Holm correction in {n_sig}/23 non-pilot participants. "
        f"The unadjusted participant-specific 95th-percentile chance thresholds ranged from {lo:.1f}\\% to {hi:.1f}\\%. "
        "These thresholds describe the null distribution; adjusted significance is determined by the Holm-corrected $p$-values, not by crossing the unadjusted threshold alone.\n"
    )
    floor_count = sum(int(r["exceedances"]) == 0 for r in primary)
    max_raw = max(float(r["p_value"]) for r in primary)
    adjusted = sorted({float(r["p_holm"]) for r in primary})
    text += (
        f"Raw primary p-values ranged from 0.0005 to {max_raw:.4f}; "
        f"{floor_count}/23 participants reached the Monte Carlo minimum of 0.0005. "
    )
    if len(adjusted) == 1:
        text += f"All primary Holm-adjusted p-values were {adjusted[0]:.4f}. "
    text += (
        "Repeated adjusted values reflect the step-down correction and finite sampling resolution, "
        "not identical effect sizes. Values at the Monte Carlo floor do not resolve smaller exact tail probabilities.\n"
    )
    (tables / "permutation_result_summary.tex").write_text(text)
    data = sorted(primary, key=lambda r: float(r["balanced_accuracy"]))
    fig, ax = plt.subplots(figsize=(8, 8))
    y = np.arange(len(data))
    ax.scatter(
        [100 * float(r["balanced_accuracy"]) for r in data],
        y,
        color="#1468b3",
        label="Observed balanced accuracy",
        s=28,
    )
    ax.scatter(
        [100 * float(r["chance_95"]) for r in data],
        y,
        facecolors="none",
        edgecolors="#222",
        marker="o",
        label="95th percentile of permutation null",
        s=30,
    )
    ax.set_yticks(y, [r["subject"] for r in data])
    ax.axvline(50, color=".6", lw=0.8, ls="--")
    ax.set(
        xlabel="Balanced accuracy (%)",
        title="Fixed eight-channel LDA: non-pilot participants",
        xlim=(40, 100),
    )
    ax.grid(axis="x", alpha=0.2)
    ax.legend(loc="lower right", fontsize=8)
    fig.tight_layout()
    fig.savefig(figures / "permutation_LDA_primary.png", dpi=180)
    plt.close(fig)
    print(text)


if __name__ == "__main__":
    main()
