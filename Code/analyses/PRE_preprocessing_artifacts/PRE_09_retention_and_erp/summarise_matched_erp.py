# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv, collections, math
import numpy as np

out = ROOT / "output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/matched_erp"


def read(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(n, rows):
    with (out / n).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


E = read(out / "response_metrics.csv")
D = read(out / "paired_response_changes.csv")
I = read(out / "matched_trial_ids.csv")
names = {"1": "BP no-FORCe", "2": "BP FORCe", "3": "Split no-FORCe", "4": "Split FORCe"}
k = lambda r: (
    r["subject"],
    r["session"],
    r["channel"],
    r["condition"],
    r["waveform"],
    r["window"],
)
idx = {k(r): r for r in E}
assert len(idx) == len(E) == 1152
assert len({(i["run"], i["trial"]) for i in I}) == len(I) == 2562
# Check the previous saved two-channel analysis exactly, before extending to all eight.
old = read(result_path("PRE_07") / "erp_metrics.csv")
for r in old:
    q = idx[
        (
            r["subject"],
            r["session"],
            r["channel"],
            r["condition"],
            "Error_minus_Correct",
            "broad_0.2_0.9",
        )
    ]
    for oldf, newf in [
        ("maxUV", "positivePeakUV"),
        ("minUV", "negativePeakUV"),
        ("rmsUV", "rmsUV"),
        ("signedPeakUV", "signedAbsPeakUV"),
        ("peakTimeSeconds", "absPeakTimeSeconds"),
    ]:
        assert abs(float(r[oldf]) - float(q[newf])) < 1e-10, (oldf, r, q)
# Same-window, same-trial comparisons. Feature-time changes can denote different extrema.
C = []
for d in D:
    a = idx[k(d)]
    b = idx[
        (
            d["subject"],
            d["session"],
            d["channel"],
            d["referenceCondition"],
            d["waveform"],
            d["window"],
        )
    ]
    c = dict(
        d,
        conditionName=names[d["condition"]],
        referenceName=names[d["referenceCondition"]],
        referenceMeanUV=b["meanUV"],
        conditionMeanUV=a["meanUV"],
        referenceNegativePeakUV=b["negativePeakUV"],
        conditionNegativePeakUV=a["negativePeakUV"],
        referenceNegativePeakTimeSeconds=b["negativePeakTimeSeconds"],
        conditionNegativePeakTimeSeconds=a["negativePeakTimeSeconds"],
        deltaNegativePeakTimeMs=1000
        * (float(a["negativePeakTimeSeconds"]) - float(b["negativePeakTimeSeconds"])),
        referenceAbsPeakTimeSeconds=b["absPeakTimeSeconds"],
        conditionAbsPeakTimeSeconds=a["absPeakTimeSeconds"],
        absolutePeakPolarityChanged=int(
            float(a["signedAbsPeakUV"]) * float(b["signedAbsPeakUV"]) < 0
        ),
    )
    C.append(c)
write("paired_erp_metrics.csv", C)
central = [
    c
    for c in C
    if c["channel"] in ["Cz", "FCz"]
    and c["waveform"] == "Error_minus_Correct"
    and c["window"] == "main_0.4_0.8"
]
write("central_channel_changes.csv", central)
summary = []
for subject in ["ALL", "mle01", "spe30"]:
    for wave in ["Correct_ND", "Error_D", "Error_minus_Correct"]:
        for condition, reference in [("2", "1"), ("4", "3"), ("3", "1"), ("4", "2")]:
            a = [
                c
                for c in C
                if (subject == "ALL" or c["subject"] == subject)
                and c["waveform"] == wave
                and c["window"] == "main_0.4_0.8"
                and c["condition"] == condition
                and c["referenceCondition"] == reference
            ]
            r = dict(
                subject=subject,
                waveform=wave,
                condition=condition,
                referenceCondition=reference,
                channelSessionComparisons=len(a),
                medianAbsMeanChangeUV=float(
                    np.median([abs(float(c["deltaMeanUV"])) for c in a])
                ),
                maxAbsMeanChangeUV=max(abs(float(c["deltaMeanUV"])) for c in a),
                medianWaveformDifferenceRmsUV=float(
                    np.median([float(c["waveformDifferenceRmsUV"]) for c in a])
                ),
                maxWaveformDifferenceUV=max(
                    float(c["waveformDifferenceMaxUV"]) for c in a
                ),
                medianAbsNegativePeakTimeChangeMs=float(
                    np.median([abs(float(c["deltaNegativePeakTimeMs"])) for c in a])
                ),
                maxAbsNegativePeakTimeChangeMs=max(
                    abs(float(c["deltaNegativePeakTimeMs"])) for c in a
                ),
                medianAbsAbsPeakTimeChangeMs=float(
                    np.median([abs(float(c["deltaAbsPeakTimeMs"])) for c in a])
                ),
                maxAbsAbsPeakTimeChangeMs=max(
                    abs(float(c["deltaAbsPeakTimeMs"])) for c in a
                ),
                absPeakPolarityChangedComparisons=sum(
                    int(c["absolutePeakPolarityChanged"]) for c in a
                ),
            )
            summary.append(r)
write("comparison_summary.csv", summary)
counts = collections.Counter((r["subject"], r["session"], r["label"]) for r in I)
L = [
    "# Matched eight-channel ErrP pilot comparison",
    "",
    "## Scope",
    "",
    "This completes the requested saved-output comparison before preparation of a research note. It does not rerun preprocessing/FORCe, change rejection rules, or create a new manuscript.",
    "",
    "The comparison uses the 29 saved boundary-pilot recordings and the same 2,562 trials accepted in all four conditions. Trial identity is recording plus original trial number; `matched_trial_ids.csv` contains the exact IDs. Each participant/session is pooled across its selected runs with equal weight per trial.",
    "",
    "Correct denotes non-displaced (label 1); Error denotes displaced (label 2). These are experimental condition labels, not independent confirmation that every displaced event elicited an error percept. Error-Correct is displaced minus non-displaced.",
    "",
    "All outputs use movement marker 400 at t=0, the same [-0.2,0) s baseline and [-1,+1) s crop. FORCe processed three separate 1 s windows in a 3 s segment, with joins at -0.5 and +0.5 s. Filtering is held constant within each FORCe/control pair:",
    "",
    "1. BP no-FORCe and BP FORCe: continuous 1–20 Hz bandpass before optional cleaning.",
    "2. Split no-FORCe and Split FORCe: continuous 1 Hz HP, optional cleaning, 20 Hz LP over the 3 s segment, then cropping.",
    "",
    "Comparing across the two filtering families evaluates the practical implementations; it does not isolate filtering order alone. The main plots use the intersection across all four, avoiding trial-selection confounding at the expense of omitting trials accepted by only some methods.",
    "",
    "## Matched trial counts and figures",
    "",
    "| Participant | Session | Correct / ND | Error / D | Eight-channel plot |",
    "|---|---|---:|---:|---|",
]
for sub in ["mle01", "spe30"]:
    for ss in ["pre", "post", "retest"]:
        L.append(
            f'| {sub} | {ss} | {counts[(sub,ss,"1")]} | {counts[(sub,ss,"2")]} | [Open](figures/{sub}_{ss}_matched_erp.png) |'
        )
L += [
    "",
    "Each figure has eight channel rows and three columns: Correct, Error, and Error-Correct. All four outputs appear on the same axes. No-FORCe is dashed, FORCe solid; black/red denote bandpass and green/blue denote split filtering. Cleaning joins are grey dotted lines; onset is black. Correct and Error share the vertical scale within each channel; the difference column has its own scale. Positive voltage is upward.",
    "",
    "## Response measurements",
    "",
    "`response_metrics.csv` contains signed mean amplitude, RMS, positive/negative extrema and their times, and the signed largest-absolute extremum and its time, for every channel/condition/waveform. The main interval is [0.4,0.8) s; [0.2,0.9) s reproduces the previous broader analysis.",
    "",
    "`paired_erp_metrics.csv` contains same-window changes with the filtering-matched controls, the filter-only contrast and the two FORCe implementations. `central_channel_changes.csv` extracts Cz/FCz Error-Correct results in the main interval.",
    "",
    "The following table summarises all eight channels and six participant/session averages (48 comparisons per row). Values are descriptive, not population-level significance tests or independent participant replicates.",
    "",
    "| Contrast (first minus second) | Median absolute mean-amplitude change (µV) | Maximum absolute mean-amplitude change (µV) | Median waveform-change RMS (µV) | Median absolute negative-extremum time change (ms) |",
    "|---|---:|---:|---:|---:|",
]
for r in summary:
    if r["subject"] == "ALL" and r["waveform"] == "Error_minus_Correct":
        L.append(
            f"| {names[r['condition']]} minus {names[r['referenceCondition']]} | {r['medianAbsMeanChangeUV']:.3f} | {r['maxAbsMeanChangeUV']:.3f} | {r['medianWaveformDifferenceRmsUV']:.3f} | {r['medianAbsNegativePeakTimeChangeMs']:.0f} |"
        )
L += [
    "",
    "Peak times are descriptive extrema within a search interval, not validated ERP-component latencies. A shifted extremum can reflect a change in which peak is largest, altered polarity, interval-edge selection, or a cleaning boundary; it need not represent a physiological delay. Smaller amplitudes or smoother traces alone cannot establish artifact removal or signal preservation.",
    "",
    "## Checks",
    "",
    "- All included samples are finite, meet saved acceptance, and have a zero mean over the baseline within numerical tolerance.",
    "- All four conditions use exactly the same trial IDs and labels.",
    "- Broader-window Cz/FCz metrics reproduce the previous saved ERP table to 1e-10 tolerance.",
    "- The separate retention/quality review remains the source for method-specific retained-trial counts and residual concerns.",
    "",
    "Reproduce by running `compare_matched_erp.m` in MATLAB, then `summarise_matched_erp.py`. The main numerical outputs and figures remain separate from the earlier notes.",
]
findings = [
    "",
    "## Interpretation of this matched pilot",
    "",
    "- The two no-FORCe controls are close in the main response interval: across 48 channel/session Error-Correct comparisons, median absolute mean-amplitude change is 0.104 microvolts and median waveform-change RMS is 0.108 microvolts.",
    "- Adding FORCe is not numerically neutral: median absolute mean-amplitude change is 0.808 microvolts for bandpass FORCe and 0.792 microvolts for split FORCe. Corresponding waveform-change RMS medians are 2.042 and 2.811 microvolts.",
    "- Split FORCe has fewer output quality-screen flags in the separate residual review, but its Error-Correct waveform changes are not smaller than bandpass FORCe in this matched summary. Fewer outliers or smoother joins therefore cannot establish better response preservation.",
    "- At FCz in spe30 pre, mean Error-Correct over 0.4–0.8 s changes from +1.859 to -1.654 microvolts with bandpass FORCe, and from +2.006 to -2.164 microvolts with split FORCe. This is a change in the sign of the window mean, not evidence that a validated ERP component reverses polarity.",
    "- Some peak-time differences reflect selection of different extrema. No population-level significance, physiological delay, or cleaner superiority is inferred from these two participants.",
    "",
    "### FCz Error-Correct mean amplitude, 0.4–0.8 s",
    "",
    "| Participant | Session | BP no-FORCe (microvolts) | BP FORCe | Split no-FORCe | Split FORCe |",
    "|---|---|---:|---:|---:|---:|",
]
for sub in ["mle01", "spe30"]:
    for ss in ["pre", "post", "retest"]:
        values = [
            float(
                idx[(sub, ss, "FCz", c, "Error_minus_Correct", "main_0.4_0.8")][
                    "meanUV"
                ]
            )
            for c in ["1", "2", "3", "4"]
        ]
        findings.append(
            "| "
            + sub
            + " | "
            + ss
            + " | "
            + " | ".join(f"{v:+.3f}" for v in values)
            + " |"
        )
findings += [
    "",
    "The completed checks support retaining no-FORCe as the primary working analysis with targeted review of concerning retained trials, and preserving FORCe as a sensitivity analysis. They do not establish that every no-FORCe trial is clean or that all FORCe-related changes are harmful. The pilot is now ready for synthesis with the input and residual-quality analyses; no further FORCe-specific optimisation is required for this comparison.",
]
findings.append("")
pos = L.index("## Checks")
L[pos:pos] = findings

(out / "README.md").write_text("\n".join(L) + "\n", encoding="utf-8")
print("\n".join(L[-17:-5]))
print(
    "VERIFIED: 2562 matched trial IDs, 1152 metric rows, prior Cz/FCz results reproduced."
)
