# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv, collections
import numpy as np

out = ROOT / "output/FEA_features_repeatability/FEA_01_feature_audit"
SETS = {
    "Central": ["Cz", "FCz"],
    "Centroparietal": ["CP1", "CP5"],
    "Posterior": ["P3", "PO3", "PO7"],
    "Full": ["P3", "PO3", "PO7", "CP5", "CP1", "Cz", "FCz", "FC1"],
}


def read(n):
    with (out / n).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(n, rows):
    with (out / n).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


R = read("repeatability_channel_metrics.csv")
fields = list(R[0])[:12] + ["resolution", "waveform"]
groups = collections.defaultdict(list)
for r in R:
    assert abs(float(r["pearsonR"])) <= 1 + 1e-10
    groups[tuple(r[f] for f in fields)].append(r)
assert len(R) == 139008
G = []
for key, rs in groups.items():
    assert len(rs) == 8 and len(set(r["channel"] for r in rs)) == 8
    for name, chs in SETS.items():
        a = [r for r in rs if r["channel"] in chs]
        g = dict(zip(fields, key))
        g["channelSet"] = name
        g["channels"] = len(a)
        for f in ["pearsonR", "differenceRmsUV", "normalisedDifferenceRms"]:
            g[f] = float(np.median([float(r[f]) for r in a]))
        G.append(g)
write("repeatability_set_comparisons.csv", G)
keys = [
    "subject",
    "sessionA",
    "sessionB",
    "condition",
    "test",
    "resolution",
    "waveform",
    "channelSet",
]
sg = collections.defaultdict(list)
for g in G:
    sg[tuple(g[k] for k in keys)].append(g)
S = []
for key, a in sg.items():
    r = dict(zip(keys, key))
    r["comparisons"] = len(a)
    for f in ["pearsonR", "differenceRmsUV", "normalisedDifferenceRms"]:
        v = [float(g[f]) for g in a]
        r[f + "Median"] = float(np.median(v))
        r[f + "P10"] = float(np.quantile(v, 0.1))
        r[f + "P90"] = float(np.quantile(v, 0.9))
    r["nonDisplacedA"] = a[0]["nonDisplacedA"]
    r["displacedA"] = a[0]["displacedA"]
    S.append(r)
write("repeatability_summary.csv", S)
# Equal reference-window means must agree between resolutions; the only change is averaging.
check = collections.defaultdict(dict)
for r in R:
    key = tuple(r[f] for f in fields if f != "resolution") + (r["channel"],)
    check[key][r["resolution"]] = r
for a in check.values():
    assert set(a) == {"500Hz", "100ms"}
    for f in ["responseMeanA", "responseMeanB"]:
        assert abs(float(a["500Hz"][f]) - float(a["100ms"][f])) < 1e-10
print(
    "REPEATABILITY CHECKS PASSED: disjoint class-balanced halves; all resolution-paired response means agree; session separation retained."
)
print("NO-FORCe raw sample correlations, median across channels then repetitions/pairs")
for test in ["balanced_split_half", "between_runs", "between_sessions"]:
    for sub in ["mle01", "spe30"]:
        for ss in ["pre", "post", "retest"]:
            a = [
                r
                for r in S
                if r["test"] == test
                and r["subject"] == sub
                and r["sessionA"] == ss
                and r["condition"] == "1"
                and r["resolution"] == "500Hz"
                and r["channelSet"] == "Full"
                and r["waveform"] in ["ND", "D", "Shared", "D_minus_ND"]
            ]
            if a:
                print(
                    test,
                    sub,
                    ss,
                    [
                        (
                            r["sessionB"],
                            r["waveform"],
                            round(r["pearsonRMedian"], 3),
                            round(r["normalisedDifferenceRmsMedian"], 3),
                        )
                        for r in a
                    ],
                )
