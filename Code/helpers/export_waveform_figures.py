"""Export primary no-FORCe participant/session figures from saved report means.

Produces one eight-channel PNG per participant/session and a combined PDF.
No individual epochs are loaded and no preprocessing or classifier is rerun.
"""

from pathlib import Path
import csv
import json
import sys
import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["pdf.fonttype"] = 42
from matplotlib.backends.backend_pdf import PdfPages

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_paths import ROOT, result_path


def main():
    report = ROOT / "output/PRE_preprocessing_artifacts/report"
    data = json.loads((report / "waveform_means.json").read_text(encoding="utf-8"))
    all_records = data["records"]
    records = sorted(
        [r for r in all_records if r["condition"] == 1 and r["selection"] == "all"],
        key=lambda r: (r["subject"], ["pre", "post", "retest"].index(r["session"])),
    )
    with (result_path("DEC_02") / "session_eligibility.csv").open(
        encoding="utf-8-sig", newline=""
    ) as f:
        status = {(r["subject"], r["session"]): r["status"] for r in csv.DictReader(f)}
    figures = report / "waveforms" / "BP_noFORCe"
    figures.mkdir(parents=True, exist_ok=True)
    times = -1 + np.arange(1000) / 500
    limits = {}
    for subject in sorted({r["subject"] for r in records}):
        extent = np.ones(8)
        for r in [r for r in all_records if r["subject"] == subject]:
            correct, error = np.asarray(r["correct"]), np.asarray(r["error"])
            for x in [correct, error, error - correct]:
                if x.size:
                    extent = np.maximum(extent, np.max(np.abs(x), axis=0))
        limits[subject] = 1.08 * extent
    with PdfPages(
        report / "BP_noFORCe_participant_waveforms.pdf",
        metadata={
            "Title": "Participant and session waveforms: primary BP no-FORCe analysis",
            "Author": "Satyam Awasthi",
        },
    ) as pdf:
        for page, r in enumerate(records, 1):
            subject, session = r["subject"], r["session"]
            correct, error = np.asarray(r["correct"]), np.asarray(r["error"])
            fig, axes = plt.subplots(4, 2, figsize=(8.27, 11.69), sharex=True)
            fig.subplots_adjust(
                left=0.09, right=0.975, bottom=0.13, top=0.865, hspace=0.40, wspace=0.22
            )
            fig.suptitle(f"{subject} / {session}: BP no-FORCe", fontsize=16, y=0.97)
            cohort = (
                "Pilot (exploratory)"
                if subject in ["mle01", "spe30"]
                else "Non-pilot participant"
            )
            fig.text(
                0.5,
                0.939,
                f"{cohort} | All accepted trials | Correct (ND) n={r['nND']}; Error (D) n={r['nD']}",
                ha="center",
                fontsize=10,
            )
            handles = None
            for ch, ax in enumerate(axes.flat):
                lines = []
                for y, color, label in [
                    (correct[:, ch], "#1468b3", "Correct (ND)"),
                    (error[:, ch], "#ce3838", "Error (D)"),
                    ((error - correct)[:, ch], "#222222", "Error - Correct"),
                ]:
                    lines += ax.plot(times, y, color=color, lw=1, label=label)
                handles = lines
                ax.axvline(0, color=".45", lw=0.7)
                ax.axhline(0, color=".7", lw=0.6)
                ax.set(
                    xlim=(-1, 1),
                    ylim=(-limits[subject][ch], limits[subject][ch]),
                    title=data["channels"][ch],
                )
                ax.set_xticks([-1, -0.5, 0, 0.5, 1])
                ax.tick_params(labelsize=8)
                ax.grid(alpha=0.18)
                ax.set_ylabel("Voltage (µV)", fontsize=8)
                if ch >= 6:
                    ax.set_xlabel("Time from movement (s)", fontsize=9)
            fig.legend(
                handles=handles,
                loc="upper center",
                bbox_to_anchor=(0.5, 0.923),
                ncol=3,
                frameon=False,
                fontsize=10,
            )
            if status[subject, session] != "ok":
                fig.text(
                    0.5,
                    0.885,
                    "Limited-data session: accepted trials shown; ineligible for classifier cross-validation.",
                    ha="center",
                    fontsize=8,
                    color="#9c3b20",
                )
            fig.text(
                0.09,
                0.042,
                "Continuous 1-20 Hz; baseline [-0.2,0) s; quality checks across the three-second context.\nSame accepted IDs as decoder preparation; no FORCe acceptance restriction. Fixed axes across sessions per channel.",
                fontsize=7.5,
            )
            fig.text(0.97, 0.018, f"{page}/{len(records)}", ha="right", fontsize=8)
            fig.savefig(figures / f"{subject}_{session}.png", dpi=150)
            pdf.savefig(fig)
            plt.close(fig)
    print(
        f"WAVEFORM FIGURES COMPLETE: {len(records)} PNGs and {len(records)} PDF pages"
    )


if __name__ == "__main__":
    main()
