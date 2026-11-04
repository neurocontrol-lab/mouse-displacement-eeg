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


W = read("trial_bin_features.csv")
T = read("timepoint_summary.csv")
features = list(W[0])[7:]
assert len(features) == 56 and len(W) == 2562 * 4
labels = [
    {
        "set": s,
        "channels": ", ".join(chs),
        "binnedFeatures": len(chs) * 7,
        "timepointFeatures": len(chs) * 350,
    }
    for s, chs in SETS.items()
]
write("channel_sets.csv", labels)
groups = collections.defaultdict(list)
for r in W:
    groups[(r["subject"], r["session"], r["condition"])].append(r)
idx = {}
mat = {}
meta = {}
F = []
for g, rs in groups.items():
    ids = [(r["run"], r["trial"]) for r in rs]
    assert len(ids) == len(set(ids))
    y = np.array([int(r["label"]) for r in rs])
    x = np.array([[float(r[f]) for f in features] for r in rs])
    mat[g] = x
    meta[g] = (ids, y)
    n1 = sum(y == 1)
    n2 = sum(y == 2)
    a = x[y == 1]
    b = x[y == 2]
    m1 = a.mean(0)
    m2 = b.mean(0)
    sd1 = a.std(0, ddof=1)
    sd2 = b.std(0, ddof=1)
    sp = np.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))
    assert np.all(sp > 1e-12)
    for j, f in enumerate(features):
        ch, start, end = f.split("_")
        lo = int(start) / 1000
        hi = int(end[:-2]) / 1000
        r = dict(
            subject=g[0],
            session=g[1],
            condition=g[2],
            channel=ch,
            binStart=lo,
            binEnd=hi,
            feature=f,
            nonDisplaced=int(n1),
            displaced=int(n2),
            meanND=m1[j],
            meanD=m2[j],
            sdND=sd1[j],
            sdD=sd2[j],
            pooledSD=sp[j],
            differenceUV=m2[j] - m1[j],
            cohenD=(m2[j] - m1[j]) / sp[j],
        )
        F.append(r)
        idx[(*g, ch, round(lo, 1))] = r
for g in groups:
    ids, y = meta[g]
    rids, ry = meta[(*g[:2], "1")]
    assert ids == rids and np.array_equal(y, ry)
assert len(F) == 1344
write("binned_feature_summary.csv", F)
raw = collections.defaultdict(list)
for t in T:
    for k in [
        "timeSeconds",
        "meanND",
        "meanD",
        "sdND",
        "sdD",
        "differenceUV",
        "cohenD",
        "pooledSD",
    ]:
        t[k] = float(t[k])
    raw[(t["subject"], t["session"], t["condition"], t["channel"])].append(t)
loss = []
setsummary = []
for g in groups:
    for ch in SETS["Full"]:
        a = raw[(*g, ch)]
        assert len(a) == 350
        for b in range(7):
            ts = a[b * 50 : (b + 1) * 50]
            f = idx[(*g, ch, round(0.2 + b * 0.1, 1))]
            assert len(ts) == 50
            for wave, col in [
                ("Correct_ND", "meanND"),
                ("Error_D", "meanD"),
                ("Error_minus_Correct", "differenceUV"),
            ]:
                v = np.array([t[col] for t in ts])
                m = float(v.mean())
                assert abs(m - f[col]) < 1e-10
                loss.append(
                    dict(
                        subject=g[0],
                        session=g[1],
                        condition=g[2],
                        channel=ch,
                        binStart=f["binStart"],
                        binEnd=f["binEnd"],
                        waveform=wave,
                        binMeanUV=m,
                        unbinnedMinUV=float(v.min()),
                        unbinnedMaxUV=float(v.max()),
                        unbinnedAbsPeakUV=float(np.abs(v).max()),
                        withinBinVariationRmsUV=float(np.sqrt(np.mean((v - m) ** 2))),
                        meanToWithinBinPeakRatio=abs(m)
                        / max(float(np.abs(v).max()), 1e-12),
                        crossesZero=int(v.min() < 0 < v.max()),
                    )
                )
    for name, chs in SETS.items():
        fs = [
            f
            for f in F
            if (f["subject"], f["session"], f["condition"]) == g and f["channel"] in chs
        ]
        ls = [
            l
            for l in loss
            if (l["subject"], l["session"], l["condition"]) == g
            and l["channel"] in chs
            and l["waveform"] == "Error_minus_Correct"
        ]
        setsummary.append(
            dict(
                subject=g[0],
                session=g[1],
                condition=g[2],
                channelSet=name,
                features=len(fs),
                medianAbsCohenD=float(np.median([abs(f["cohenD"]) for f in fs])),
                maxAbsCohenD=max(abs(f["cohenD"]) for f in fs),
                meanDifferenceRmsUV=float(
                    np.sqrt(np.mean([f["differenceUV"] ** 2 for f in fs]))
                ),
                withinBinVariationRmsUV=float(
                    np.sqrt(np.mean([l["withinBinVariationRmsUV"] ** 2 for l in ls]))
                ),
                medianMeanToWithinBinPeakRatio=float(
                    np.median([l["meanToWithinBinPeakRatio"] for l in ls])
                ),
                binsWithSignChanges=sum(l["crossesZero"] for l in ls),
            )
        )
write("binning_detail_loss.csv", loss)
write("set_feature_summary.csv", setsummary)
rawsets = []
for g in groups:
    for name, chs in SETS.items():
        rs = [
            r
            for r in T
            if (r["subject"], r["session"], r["condition"]) == g and r["channel"] in chs
        ]
        rawsets.append(
            dict(
                subject=g[0],
                session=g[1],
                condition=g[2],
                channelSet=name,
                features=len(rs),
                medianAbsCohenD=float(np.median([abs(r["cohenD"]) for r in rs])),
                maxAbsCohenD=max(abs(r["cohenD"]) for r in rs),
            )
        )
write("set_timepoint_summary.csv", rawsets)
# Processing effects on the same single-trial scalar feature, not on selected means alone.
paired = []
for sub, ss, _ in groups:
    for c, ref in [("2", "1"), ("4", "3"), ("3", "1"), ("4", "2")]:
        g = (sub, ss, c)
        rg = (sub, ss, ref)
        if any(
            r["subject"] == sub
            and r["session"] == ss
            and r["condition"] == c
            and r["referenceCondition"] == ref
            for r in paired
        ):
            continue
        a = mat[g]
        b = mat[rg]
        e = a - b
        for j, f in enumerate(features):
            ch, start, end = f.split("_")
            lo = int(start) / 1000
            fa = idx[(*g, ch, round(lo, 1))]
            fb = idx[(*rg, ch, round(lo, 1))]
            fixed = idx[(sub, ss, "1", ch, round(lo, 1))]["pooledSD"]
            rho = float(np.corrcoef(a[:, j], b[:, j])[0, 1])
            assert np.isfinite(rho)
            paired.append(
                dict(
                    subject=sub,
                    session=ss,
                    condition=c,
                    referenceCondition=ref,
                    channel=ch,
                    feature=f,
                    binStart=lo,
                    binEnd=int(end[:-2]) / 1000,
                    matchedTrials=len(a),
                    meanChangeUV=float(e[:, j].mean()),
                    pairedChangeRmsUV=float(np.sqrt(np.mean(e[:, j] ** 2))),
                    pairedChangeRmsInControlSD=float(np.sqrt(np.mean(e[:, j] ** 2)))
                    / fixed,
                    trialPearsonR=rho,
                    conditionCohenD=fa["cohenD"],
                    referenceCohenD=fb["cohenD"],
                    deltaCohenD=fa["cohenD"] - fb["cohenD"],
                )
            )
write("paired_feature_changes.csv", paired)
PS = []
for name, chs in SETS.items():
    for c, ref in [("2", "1"), ("4", "3"), ("3", "1"), ("4", "2")]:
        a = [
            r
            for r in paired
            if r["channel"] in chs
            and r["condition"] == c
            and r["referenceCondition"] == ref
        ]
        PS.append(
            dict(
                channelSet=name,
                condition=c,
                referenceCondition=ref,
                featureSessionComparisons=len(a),
                medianTrialPearsonR=float(np.median([r["trialPearsonR"] for r in a])),
                medianPairedChangeRmsUV=float(
                    np.median([r["pairedChangeRmsUV"] for r in a])
                ),
                medianPairedChangeRmsInControlSD=float(
                    np.median([r["pairedChangeRmsInControlSD"] for r in a])
                ),
                medianAbsDeltaCohenD=float(
                    np.median([abs(r["deltaCohenD"]) for r in a])
                ),
            )
        )
write("set_processing_summary.csv", PS)
assert len(paired) == 1344 and len(loss) == 4032 and len(setsummary) == 96
print(
    "FEATURE CHECKS PASSED: exact 2562 matched IDs; 56 scalar features; every bin has 50 samples; binned class means reproduce averages of 500 Hz class means within 1e-10."
)
print("SET PROCESSING SUMMARY")
for r in PS:
    print(r)
print("BIN DETAIL LOSS: no-FORCe, participant/session-specific")
for r in setsummary:
    if r["condition"] == "1":
        print(r)
