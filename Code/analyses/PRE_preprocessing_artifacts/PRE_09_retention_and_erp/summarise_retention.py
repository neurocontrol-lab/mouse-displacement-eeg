# Resolve inputs/results by permanent experiment ID, independent of cwd.
import sys
from pathlib import Path

_CODE = next(p for p in Path(__file__).resolve().parents if p.name == "Code")
sys.path.insert(0, str(_CODE))
from research_paths import ROOT, result_path, code_path
import csv, collections, json

root = ROOT
out = ROOT / "output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/quality"


def read(p):
    with p.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write(name, rows):
    with (out / name).open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def yes(x):
    return str(x).lower() in ("true", "1")


flags = [
    "lowFrequencyFlag",
    "highFrequencyFlag",
    "localAbruptFlag",
    "amplitudeScreen",
    "lineDominant",
    "grossExcursion",
]
T = read(
    root
    / "output/PRE_preprocessing_artifacts/PRE_08_input_quality/trial_screen_and_review.csv"
)
F = read(
    root
    / "output/PRE_preprocessing_artifacts/PRE_08_input_quality/window_channel_metrics.csv"
)
D = read(out / "saved_trial_decisions.csv")
for t in T:
    t["anyInputFlag"] = int(any(yes(t[f]) for f in flags))
key = lambda r: (r["run"], r["trial"])
index = {key(t): t for t in T}
assert len(index) == len(T) == 2799
by = collections.defaultdict(list)
for f in F:
    by[key(f)].append(f)
for k, fs in by.items():
    assert len(fs) == 24
lookup = {}
for d in D:
    k = (d["run"], d["trial"], d["condition"])
    assert k not in lookup
    lookup[k] = d
    assert yes(d["eligible"]) == (key(d) in index)
    if key(d) in index:
        assert d["label"] == index[key(d)]["label"]
assert len(D) == 2915 * 4
linked = []
for d in D:
    t = index.get(key(d))
    a = dict(d)
    a["trialClass"] = (
        "non-displaced"
        if d["label"] == "1"
        else "displaced" if d["label"] == "2" else "unlabelled"
    )
    a["inputScreenAvailable"] = int(t is not None)
    for flag in flags:
        a[flag] = t[flag] if t else ""
    a["anyInputFlag"] = int(any(yes(t[f]) for f in flags)) if t else ""
    a["inputPeakAbsUV"] = t["inputPeakAbsUV"] if t else ""
    a["maxHighZ"] = t["maxHighZ"] if t else ""
    a["maxLowZ"] = t["maxLowZ"] if t else ""
    a["flaggedWindowIntersectsAnalysis"] = (
        int(
            any(
                any(yes(f[g]) for g in flags[:-1])
                and float(f["endSeconds"]) > -1
                and float(f["startSeconds"]) < 1
                for f in by[key(d)]
            )
        )
        if t
        else ""
    )
    a["flaggedWindowIntersectsResponse"] = (
        int(
            any(
                any(yes(f[g]) for g in flags[:-1]) and yes(f["responseWindowOverlap"])
                for f in by[key(d)]
            )
        )
        if t
        else ""
    )
    linked.append(a)
write("trial_flag_decisions.csv", linked)
# Preserve exact channel and one-second location for every flagged feature.
WF = []
for f in F:
    if not any(yes(f[g]) for g in flags[:-1]):
        continue
    a = dict(f)
    for c in range(1, 5):
        d = lookup[(f["run"], f["trial"], str(c))]
        a[f"condition{c}Accepted"] = d["accepted"]
        a[f"condition{c}Reason"] = d["reason"]
    WF.append(a)
write("flagged_channel_windows.csv", WF)
# Trial-level summaries for each group and trial class; feature counts overlap.
summary = []
reasons = []
for level, groupfields in [
    ("pilot", []),
    ("participant", ["subject"]),
    ("session", ["subject", "session"]),
    ("run", ["subject", "session", "runNumber", "run"]),
]:
    groups = collections.defaultdict(list)
    for d in linked:
        groups[tuple(d[f] for f in groupfields) + (d["condition"],)].append(d)
    for group, allrows in groups.items():
        for trialclass in ["ALL", "non-displaced", "displaced"]:
            rows = [
                d
                for d in allrows
                if trialclass == "ALL" or d["trialClass"] == trialclass
            ]
            eligible = [d for d in rows if yes(d["eligible"])]
            acc = [d for d in eligible if yes(d["accepted"])]
            meta = {
                "level": level,
                "subject": "ALL",
                "session": "ALL",
                "runNumber": "ALL",
                "run": "ALL",
                "trialClass": trialclass,
                "condition": group[-1],
                "conditionName": allrows[0]["conditionName"],
            }
            meta.update(dict(zip(groupfields, group[:-1])))
            row = dict(
                meta,
                trialRows=len(rows),
                eligibleTrials=len(eligible),
                acceptedTrials=len(acc),
                rejectedEligibleTrials=len(eligible) - len(acc),
                unavailableInputTrials=len(rows) - len(eligible),
            )
            for flag in ["anyInputFlag"] + flags + ["flaggedWindowIntersectsResponse"]:
                flagged = [d for d in eligible if yes(d[flag])]
                kept = [d for d in flagged if yes(d["accepted"])]
                row[flag + "InputTrials"] = len(flagged)
                row[flag + "AcceptedTrials"] = len(kept)
                row[flag + "RejectedTrials"] = len(flagged) - len(kept)
            summary.append(row)
            for reason, num in collections.Counter(
                d["reason"] for d in rows if not yes(d["accepted"])
            ).items():
                reasons.append(dict(meta, reason=reason, trials=num))
write("retention_by_group_and_flag.csv", summary)
write("rejection_reasons.csv", reasons)
# Expose all accepted flagged inputs for review, not just selected illustrations.
kept = [d for d in linked if yes(d["accepted"]) and yes(d["anyInputFlag"])]
write("accepted_flagged_trials.csv", kept)
paired = []
for c1, c2 in [(1, 2), (1, 3), (3, 4)]:
    for subject in ["ALL", "mle01", "spe30"]:
        for flag in ["ALL", "anyInputFlag"] + flags:
            ts = [
                t
                for t in T
                if (subject == "ALL" or t["subject"] == subject)
                and (flag == "ALL" or yes(t[flag]))
            ]
            bins = collections.Counter(
                (
                    yes(lookup[(*key(t), str(c1))]["accepted"]),
                    yes(lookup[(*key(t), str(c2))]["accepted"]),
                )
                for t in ts
            )
            paired.append(
                {
                    "subject": subject,
                    "firstCondition": c1,
                    "secondCondition": c2,
                    "inputFlag": flag,
                    "inputTrials": len(ts),
                    "bothAccepted": bins[(True, True)],
                    "firstOnlyAccepted": bins[(True, False)],
                    "secondOnlyAccepted": bins[(False, True)],
                    "bothRejected": bins[(False, False)],
                }
            )
write("paired_decision_counts.csv", paired)
# Deterministic review selection among accepted flagged inputs, plus gross cases.
selected = []
seen = set()
for sub in ["mle01", "spe30"]:
    for flag, metric in [
        ("grossExcursion", "inputPeakAbsUV"),
        ("lowFrequencyFlag", "maxLowZ"),
        ("highFrequencyFlag", "maxHighZ"),
        ("localAbruptFlag", "inputPeakAbsUV"),
        ("lineDominant", "inputPeakAbsUV"),
    ]:
        cand = [
            d
            for d in kept
            if d["subject"] == sub and d["condition"] in ["1", "3"] and yes(d[flag])
        ]
        if cand:
            d = max(cand, key=lambda d: float(d[metric]))
            k = key(d)
            if k not in seen:
                seen.add(k)
                selected.append(
                    dict(d, selection=flag + " retained by " + d["conditionName"])
                )
for sub in ["mle01", "spe30"]:
    cand = [
        d
        for d in kept
        if d["subject"] == sub
        and d["condition"] in ["1", "3"]
        and yes(d["flaggedWindowIntersectsResponse"])
    ]
    if cand:
        d = max(cand, key=lambda d: float(d["responsePeakAbsUV"]))
        if key(d) not in seen:
            seen.add(key(d))
            selected.append(
                dict(
                    d,
                    selection="retained response-overlap flag; largest final response amplitude",
                )
            )
for d in sorted(
    [d for d in linked if d["condition"] == "1" and yes(d["grossExcursion"])],
    key=lambda d: float(d["inputPeakAbsUV"]),
    reverse=True,
)[:1]:
    if key(d) not in seen:
        seen.add(key(d))
        selected.append(dict(d, selection="largest gross input: inspect rejection"))
for i, d in enumerate(selected, 1):
    d["reviewID"] = i
    d["figure"] = f"accepted_review_{i:02d}.png"
write("review_selection.csv", selected)
lines = [
    "# Input flags mapped to final trial decisions",
    "",
    "This analysis links existing input-only screens to the saved four-condition boundary pilot. No cleaning is rerun and no new rejection thresholds are applied.",
    "",
    "## Conditions",
    "",
    "1. BP control: continuous 1–20 Hz, no FORCe.",
    "2. BP FORCe: same bandpass, three separate 1 s FORCe windows.",
    "3. Split control: continuous 1 Hz high-pass, segment-level 20 Hz low-pass, no FORCe.",
    "4. Split FORCe: same split filtering with three 1 s FORCe windows (additional reference).",
    "",
    "All use the same 3 s eligible segments, crop to [-1,1) s, a [-0.2,0) baseline and the saved final 100 µV amplitude rule. The cleaning boundaries are -0.5 and +0.5 s.",
    "",
    "## Mapping checks",
    "",
    "- All 2,799 input-screened trials matched by recording and original trial ID, with identical condition labels and eligibility.",
    "- All 2,915 original trial rows are represented in every condition; 116 were ineligible and do not have input screens.",
    "- Accepted flagged inputs are review candidates, not proven artifacts missed by rejection. A feature can be attenuated by filtering or cleaning, or fall partly in cropped padding.",
    "",
    "## Participant summary",
    "",
    "| Participant | Condition | Accepted / eligible | Any flag retained / input flagged | >1 mV input retained | Slow retained | HF retained | Local retained | Line retained |",
    "|---|---|---:|---:|---:|---:|---:|---:|---:|",
]
for r in summary:
    if r["level"] == "participant" and r["trialClass"] == "ALL":
        lines.append(
            f"| {r['subject']} | {r['conditionName']} | {r['acceptedTrials']} / {r['eligibleTrials']} | {r['anyInputFlagAcceptedTrials']} / {r['anyInputFlagInputTrials']} | {r['grossExcursionAcceptedTrials']} | {r['lowFrequencyFlagAcceptedTrials']} | {r['highFrequencyFlagAcceptedTrials']} | {r['localAbruptFlagAcceptedTrials']} | {r['lineDominantAcceptedTrials']} |"
        )
lines += [
    "",
    "Flag categories overlap. The >1 mV screen is based on the full high-pass input, not the final bandpassed waveform. HF flags before the final low-pass cannot be interpreted as persistent HF contamination afterwards.",
    "",
    "## Outputs",
    "",
    "- `trial_flag_decisions.csv`: every trial, condition, decision/reason, input flags and final amplitude/step measurements.",
    "- `retention_by_group_and_flag.csv`: pilot, participant, session and run summaries, each pooled and separated into displaced/non-displaced trials.",
    "- `rejection_reasons.csv`: separate amplitude, FORCe prechecks/failures and unavailable-input reasons.",
    "- `accepted_flagged_trials.csv`: complete list of retained flagged inputs for inspection.",
    "- `flagged_channel_windows.csv`: exact input channel, one-second location, flag and decisions in each condition.",
    "- `paired_decision_counts.csv`: same-trial acceptance agreement and discordance.",
    "- `review_selection.csv` and `figures/`: selected concerning inputs with final outputs for visual review.",
    "",
    "The data answer which flagged inputs remain in the accepted set. Expert inspection and output-specific evidence are still needed before calling retained signals contamination.",
]
(out / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines[20:38]))
print("Review examples:", len(selected))
print(
    "Mapping complete",
    len(D),
    "decisions;",
    len(kept),
    "accepted flagged condition/trial pairs",
)
