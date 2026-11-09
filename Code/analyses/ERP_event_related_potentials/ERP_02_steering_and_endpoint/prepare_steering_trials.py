"""Select EEG-accepted displaced reaches and match early/no-early trials."""

from collections import defaultdict
import csv
import gzip
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from helpers.erp_matching import match_by_timing
from research_paths import code_path, result_path


def rows(path):
    reader = gzip.open if path.suffix == ".gz" else open
    with reader(path, "rt", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def write(path, records):
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def select_trials():
    audit = result_path("AUD_02")
    behavior = {(r["run"], r["trial"]): r for r in rows(audit / "trial_audit.csv.gz")}
    timing = {
        (r["run"], r["trial"]): r
        for r in rows(result_path("AUD_01") / "observed_onsets.csv.gz")
    }
    trials = []
    for accepted in rows(result_path("DEC_02") / "trial_metadata.csv"):
        if accepted["label"] != "2":
            continue
        key = accepted["run"], accepted["trial"]
        b, t = behavior[key], timing[key]
        assert b["eeg_accepted"] == "1" and b["condition"] == "D" and t["label"] == "2"
        jump_samples = int(t["jump_eeg_sample"])-int(t["movement_eeg_sample"])
        steer = b["outward_steering_ms_from_jump"]
        offset = jump_samples + int(np.floor(float(steer)/2 + .5)) if steer else None
        # PRE_01 stores sample offsets -500 to 499 at 500 Hz.
        assert 0 < jump_samples <= 250
        trials.append(dict(
            run=key[0], trial=int(key[1]), subject=b["subject"], session=b["session"], cohort=accepted["cohort"],
            side=int(b["jump_direction"]), steering_250=b["steering_250"],
            reaction_ms=int(t["movement_eeg_ms_from_target"]), jump_delay_samples=jump_samples,
            steering_ms_from_jump=steer, steering_offset_samples=offset,
            steering_eeg_eligible=int(offset is not None and 0 <= offset <= 250),
            endpoint_distance_px=b["endpoint_distance_px"], closest_distance_px=b["closest_distance_px"],
            distance_eligible=int(b["manuscript_endpoint_in_outward"]),
            outward_end_reason=b["outward_end_reason"],
        ))
    return sorted(trials, key=lambda r: (r["run"], r["trial"]))


def match_steering(trials):
    grouped = defaultdict(list)
    for trial in trials:
        grouped[trial["run"], trial["side"]].append(trial)
    pairs = []
    for (run, side), group in sorted(grouped.items()):
        early = [r for r in group if r["steering_250"] == "early"]
        controls = [r for r in group if r["steering_250"] in {"late", "not_detected"}]
        if not early or not controls:
            continue
        for i, j, (reaction_gap, jump_delay_gap) in match_by_timing(early, controls):
            a, b = early[i], controls[j]
            pairs.append(dict(
                subject=a["subject"], session=a["session"], cohort=a["cohort"], run=run, side=side,
                trial_early=a["trial"], trial_control=b["trial"], control_group=b["steering_250"],
                reaction_gap_ms=int(reaction_gap), jump_delay_gap_ms=int(jump_delay_gap),
            ))
    used = {(p["run"], p[key]) for p in pairs for key in ("trial_early", "trial_control")}
    assert len(used) == 2*len(pairs)
    return pairs


def main():
    out = result_path("ERP_02")
    out.mkdir(parents=True, exist_ok=True)
    trials = select_trials()
    pairs = match_steering(trials)
    old = json.loads((code_path("ERP_01") / "windows.json").read_text(encoding="utf-8"))
    windows = [{k: v for k, v in r.items() if k != "expected_sign"}
               for r in old if r["alignment"] == "jump"]
    windows.append(dict(alignment="jump", component_window="Posterior positivity",
                        electrodes=["P3","PO3","PO7"], start_ms=200, end_ms_exclusive=400))
    write(out / "trial_selection.csv", trials)
    write(out / "steering_pairs.csv", pairs)
    (out / "windows.json").write_text(json.dumps(windows, indent=2)+"\n", encoding="utf-8")
    print(f"{len(trials):,} accepted D trials; {len(pairs):,} same-run and same-side pairs")
    print(f"{sum(t['steering_eeg_eligible'] for t in trials):,} detections with full steering-aligned support")


if __name__ == "__main__":
    main()
