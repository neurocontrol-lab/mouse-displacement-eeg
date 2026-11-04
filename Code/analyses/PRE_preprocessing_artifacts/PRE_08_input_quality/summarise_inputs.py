# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv, random, math, json
import numpy as np

root = ROOT / "output/PRE_preprocessing_artifacts/PRE_08_input_quality"


def read(name):
    with (root / name).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (root / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def truth(x):
    return x.lower() in ("1", "true")


F = read("window_channel_metrics.csv")
T = read("trial_inventory.csv")
I = read("recording_inventory.csv")
flags = [
    "lowFrequencyFlag",
    "highFrequencyFlag",
    "localAbruptFlag",
    "amplitudeScreen",
    "lineDominant",
]
key = lambda r: (r["run"], r["trial"])
by = {key(t): [] for t in T}
for f in F:
    by[key(f)].append(f)
for t in T:
    a = by[key(t)]
    for k in flags:
        t[k] = int(any(truth(x[k]) for x in a))
        t[k + "ResponseOverlap"] = int(
            any(truth(x[k]) and truth(x["responseWindowOverlap"]) for x in a)
        )
    t["grossExcursion"] = int(float(t["inputPeakAbsUV"]) > 1000)
    t["maxHighZ"] = max(float(x["highZ"]) for x in a)
    t["maxLowZ"] = max(float(x["lowZ"]) for x in a)
    t["expertSuspectedType"] = ""
    t["expertConfidence"] = ""
    t["expertResponseOverlap"] = ""
    t["expertNotes"] = ""
write("trial_screen_and_review.csv", T)
summary = []
for sub, ss, r in (
    [(s, "ALL", "ALL") for s in ["mle01", "spe30"]]
    + [(s, ss, "ALL") for s in ["mle01", "spe30"] for ss in ["pre", "post", "retest"]]
    + [(x["subject"], x["session"], x["runNumber"]) for x in I]
):
    a = [
        t
        for t in T
        if t["subject"] == sub
        and (ss == "ALL" or t["session"] == ss)
        and (r == "ALL" or t["runNumber"] == r)
    ]
    row = {
        "subject": sub,
        "session": ss,
        "runNumber": r,
        "eligibleTrials": len(a),
        "boundedInputTrials": sum(float(t["inputPeakAbsUV"]) <= 100 for t in a),
        "grossExcursionTrials": sum(t["grossExcursion"] for t in a),
    }
    for k in flags:
        row[k + "Trials"] = sum(t[k] for t in a)
        row[k + "ResponseWindowOverlapTrials"] = sum(
            t[k + "ResponseOverlap"] for t in a
        )
    for k in ["lowFrequencyFlag", "highFrequencyFlag", "localAbruptFlag"]:
        row[k + "BoundedTrials"] = sum(
            t[k] for t in a if float(t["inputPeakAbsUV"]) <= 100
        )
    summary.append(row)
write("screen_summary.csv", summary)
rng = random.Random(20261011)
selected = []
for i in I:
    a = [t for t in T if t["run"] == i["run"]]
    t = dict(rng.choice(a))
    t["selection"] = "Representative"
    selected.append(t)
for title, sub, metric, bounded in [
    ("Gross excursion", "ALL", "inputPeakAbsUV", False),
    ("Higher-frequency review", "mle01", "maxHighZ", True),
    ("Higher-frequency review", "spe30", "maxHighZ", True),
    ("Slow-deflection outlier", "mle01", "maxLowZ", True),
    ("Slow-deflection outlier", "spe30", "maxLowZ", True),
    ("Line-frequency dominated", "ALL", "lineFraction", False),
]:
    a = [
        t
        for t in T
        if (sub == "ALL" or t["subject"] == sub)
        and (not bounded or float(t["inputPeakAbsUV"]) <= 100)
    ]
    if metric == "lineFraction":
        t = max(
            [t for t in a if float(t["inputPeakAbsUV"]) <= 1000],
            key=lambda t: max(float(f["lineFraction"]) for f in by[key(t)]),
        )
    else:
        t = max(a, key=lambda t: float(t[metric]))
    z = dict(t)
    z["selection"] = title
    selected.append(z)
for n, t in enumerate(selected):
    t["reviewID"] = n + 1
    t["figure"] = "review_%03d.png" % (n + 1)
write("review_selection.csv", selected)
brief = {
    "trials": len(T),
    "windows": len(T) * 3,
    "channelWindows": len(F),
    "records": len(I),
    "summaries": summary[:8],
    "targetRelativeQuantiles": np.quantile(
        [float(t["targetRelativeSeconds"]) for t in T], [0, 0.5, 1]
    ).tolist(),
    "largestInputUV": max(float(t["inputPeakAbsUV"]) for t in T),
    "grossTrials": sum(t["grossExcursion"] for t in T),
    "representativeReviewTrials": 29,
    "enrichedReviewTrials": 6,
    "eligibleHasMissing": any(not math.isfinite(float(f["highRmsUV"])) for f in F),
}
(root / "summary.json").write_text(json.dumps(brief, indent=2), encoding="utf-8")
print(json.dumps(brief, indent=2))
print(
    "ENRICHED EXAMPLES",
    [
        (
            t["reviewID"],
            t["selection"],
            t["subject"],
            t["session"],
            t["runNumber"],
            t["trial"],
            t["inputPeakAbsUV"],
        )
        for t in selected[29:]
    ],
)
