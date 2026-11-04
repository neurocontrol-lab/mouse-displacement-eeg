# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv, collections, random
import numpy as np

out = ROOT / "output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/quality"


def read(n):
    with (out / n).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(n, rows):
    with (out / n).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def yes(x):
    return str(x).lower() in ("1", "true")


key = lambda r: (r["run"], r["trial"])
ckey = lambda r: (r["run"], r["trial"], r["channel"])
F = []
with (result_path("PRE_08") / "window_channel_metrics.csv").open(
    encoding="utf-8-sig", newline=""
) as f:
    F = list(csv.DictReader(f))
original_channels = collections.defaultdict(set)
for f in F:
    for flag in ["lowFrequencyFlag", "highFrequencyFlag", "localAbruptFlag"]:
        if yes(f[flag]):
            original_channels[(*key(f), flag)].add(f["channel"])
D = read("trial_flag_decisions.csv")
Q = read("final_channel_metrics.csv")
dec = {(d["run"], d["trial"], d["condition"]): d for d in D}
features = {"lowRmsUV": "lowZ", "rangeUV": "rangeZ", "maxStepUV": "stepZ"}
refs = collections.defaultdict(list)
for q in Q:
    for f in list(q)[9:]:
        q[f] = float(q[f])
    if q["condition"] == "1" and yes(q["accepted"]):
        refs[(q["subject"], q["session"], q["channel"])].append(q)
stats = {}
for group, rs in refs.items():
    for f in features:
        v = np.log10(np.maximum([r[f] for r in rs], 1e-12))
        med = float(np.median(v))
        mad = float(np.median(np.abs(v - med)))
        assert len(v) >= 30 and mad > 1e-12
        stats[(group, f)] = (len(v), med, mad)
by = collections.defaultdict(list)
metricidx = {}
for q in Q:
    if q["condition"] == "0":
        metricidx[(*ckey(q), "0")] = q
        continue
    for f, z in features.items():
        n, med, mad = stats[((q["subject"], q["session"], q["channel"]), f)]
        q[z] = 0.67448975 * (np.log10(max(q[f], 1e-12)) - med) / mad
    q["residualLowFlag"] = int(q["lowZ"] > 3.5)
    q["residualRangeFlag"] = int(q["rangeZ"] > 3.5)
    q["residualLocalFlag"] = int(q["stepZ"] > 3.5 and q["spatialRangeRatio"] >= 3)
    q["boundaryExcessRatio"] = max(q["joinMinusStepUV"], q["joinPlusStepUV"]) / max(
        q["ordinaryStepP95UV"], 1e-12
    )
    q["boundaryReviewFlag"] = int(q["boundaryExcessRatio"] > 3)
    q["outputReviewFlag"] = int(
        any(q[f] for f in ["residualLowFlag", "residualRangeFlag", "residualLocalFlag"])
    )
    by[(*key(q), q["condition"])].append(q)
    metricidx[(*ckey(q), q["condition"])] = q
scored = [q for q in Q if q["condition"] != "0"]
write("final_channel_screen.csv", scored)
refrows = []
for (group, f), (n, med, mad) in stats.items():
    refrows.append(
        dict(
            subject=group[0],
            session=group[1],
            channel=group[2],
            feature=f,
            referenceAcceptedTrials=n,
            log10Median=med,
            log10MAD=mad,
        )
    )
write("final_screen_reference.csv", refrows)
T = []
flags = [
    "residualLowFlag",
    "residualRangeFlag",
    "residualLocalFlag",
    "boundaryReviewFlag",
    "outputReviewFlag",
]
for d in D:
    a = by.get((d["run"], d["trial"], d["condition"]), [])
    if not a:
        continue
    r = dict(d)
    for f in flags:
        r[f] = int(any(q[f] for q in a))
    for f in ["lowZ", "rangeZ", "stepZ", "boundaryExcessRatio"]:
        r["finalMax" + f[0].upper() + f[1:]] = max(q[f] for q in a)
    r["priorityChannel"] = max(a, key=lambda q: max(q["lowZ"], q["rangeZ"]))["channel"]
    T.append(r)
write("final_trial_screen.csv", T)
ti = {(*key(t), t["condition"]): t for t in T}
summary = []
for level, fields in [
    ("participant", ["subject"]),
    ("session", ["subject", "session"]),
    ("run", ["subject", "session", "runNumber", "run"]),
]:
    groups = collections.defaultdict(list)
    for t in T:
        if yes(t["accepted"]):
            groups[tuple(t[f] for f in fields) + (t["condition"],)].append(t)
    for g, rs in groups.items():
        for trialclass in ["ALL", "non-displaced", "displaced"]:
            a = [t for t in rs if trialclass == "ALL" or t["trialClass"] == trialclass]
            r = dict(
                level=level,
                subject="ALL",
                session="ALL",
                runNumber="ALL",
                run="ALL",
                condition=g[-1],
                trialClass=trialclass,
                acceptedTrials=len(a),
            )
            r.update(dict(zip(fields, g[:-1])))
            for f in flags:
                r[f + "Trials"] = sum(yes(t[f]) for t in a)
            r["inputFlaggedAcceptedTrials"] = sum(yes(t["anyInputFlag"]) for t in a)
            r["inputFlaggedOutputFlaggedTrials"] = sum(
                yes(t["anyInputFlag"]) and yes(t["outputReviewFlag"]) for t in a
            )
            r["inputUnflaggedOutputFlaggedTrials"] = sum(
                not yes(t["anyInputFlag"]) and yes(t["outputReviewFlag"]) for t in a
            )
            summary.append(r)
write("final_quality_summary.csv", summary)
# Compare the same source feature/channel after filtering and cleaning; all are identical two-second metrics.
paired = []
for sub in ["mle01", "spe30"]:
    for c, control in [("1", "0"), ("3", "0"), ("2", "1"), ("4", "3")]:
        for typ, orig in [
            ("low", "lowFrequencyFlag"),
            ("high", "highFrequencyFlag"),
            ("local", "localAbruptFlag"),
        ]:
            pairs = []
            outflagged = 0
            newflags = 0
            matched = 0
            for t in T:
                if t["subject"] != sub or t["condition"] != c or not yes(t["accepted"]):
                    continue
                ref = ti.get((*key(t), control)) if control != "0" else None
                if control != "0" and (ref is None or not yes(ref["accepted"])):
                    continue
                matched += 1
                if ref is not None:
                    newflags += yes(t["outputReviewFlag"]) and not yes(
                        ref["outputReviewFlag"]
                    )
                if not yes(t[orig]):
                    continue
                feature = {
                    "low": "lowRmsUV",
                    "high": "highRmsUV",
                    "local": "maxStepUV",
                }[typ]
                # Largest corresponding input feature channel, then same channel in output/control.
                channels = [
                    q
                    for q in by[(*key(t), c)]
                    if q["channel"] in original_channels[(*key(t), orig)]
                ]
                assert channels
                ch = max(channels, key=lambda q: metricidx[(*ckey(q), "0")][feature])[
                    "channel"
                ]
                a = metricidx[(*key(t), ch, c)]
                b = metricidx[(*key(t), ch, control)]
                pairs.append(a[feature] / max(b[feature], 1e-12))
                outflagged += yes(t["outputReviewFlag"])
            paired.append(
                dict(
                    subject=sub,
                    condition=c,
                    referenceCondition=control,
                    inputFlagType=typ,
                    matchedAcceptedTrials=matched,
                    inputFlaggedMatchedTrials=len(pairs),
                    medianFeatureRatio=float(np.median(pairs)) if pairs else "",
                    inputFlaggedWithAnyOutputFlag=outflagged,
                    newOutputFlagTrialsVersusControl=newflags,
                )
            )
write("paired_final_features.csv", paired)
# Focused flagged examples plus a reproducible sample unflagged at input in each session.
S = []
seen = set()
rng = random.Random(20261021)


def select(t, why):
    k = key(t)
    if k not in seen:
        seen.add(k)
        S.append(dict(t, selection=why))


for sub in ["mle01", "spe30"]:
    for inp, res, score in [
        ("lowFrequencyFlag", "residualLowFlag", "finalMaxLowZ"),
        ("localAbruptFlag", "residualLocalFlag", "finalMaxStepZ"),
        ("highFrequencyFlag", "outputReviewFlag", "finalMaxRangeZ"),
    ]:
        a = [
            t
            for t in T
            if t["subject"] == sub
            and t["condition"] in ["1", "3"]
            and yes(t["accepted"])
            and yes(t[inp])
        ]
        if a:
            select(
                max(a, key=lambda t: (yes(t[res]), float(t[score]))),
                "retained input " + inp + "; inspect final feature",
            )
    # Output candidates absent at input and changes after cleaning, when available.
    a = [
        t
        for t in T
        if t["subject"] == sub
        and t["condition"] in ["1", "3"]
        and yes(t["accepted"])
        and not yes(t["anyInputFlag"])
        and yes(t["outputReviewFlag"])
    ]
    if a:
        select(
            max(
                a,
                key=lambda t: max(float(t["finalMaxLowZ"]), float(t["finalMaxRangeZ"])),
            ),
            "input unflagged; final-output review flag",
        )
    a = [
        t
        for t in T
        if t["subject"] == sub
        and t["condition"] in ["2", "4"]
        and yes(t["accepted"])
        and (*key(t), str(int(t["condition"]) - 1)) in ti
        and yes(ti[(*key(t), str(int(t["condition"]) - 1))]["accepted"])
        and yes(t["outputReviewFlag"])
        and not yes(ti[(*key(t), str(int(t["condition"]) - 1))]["outputReviewFlag"])
    ]
    if a:
        select(
            max(
                a,
                key=lambda t: max(float(t["finalMaxLowZ"]), float(t["finalMaxRangeZ"])),
            ),
            "output review flag after FORCe; absent in matched control",
        )
    for ss in ["pre", "post", "retest"]:
        a = [
            t
            for t in T
            if t["subject"] == sub
            and t["session"] == ss
            and t["condition"] == "1"
            and yes(t["accepted"])
            and not yes(t["anyInputFlag"])
            and key(t) not in seen
        ]
        if a:
            select(rng.choice(a), "random input-unflagged accepted trial; " + ss)
for i, s in enumerate(S, 1):
    s["reviewID"] = i
    s["figure"] = f"accepted_review_{i:02d}.png"
write("residual_review_selection.csv", S)
print("FINAL OUTPUT SCREEN SUMMARY")
for r in summary:
    if r["level"] == "participant" and r["trialClass"] == "ALL":
        print(r)
print("Selected", len(S), "review trials")
