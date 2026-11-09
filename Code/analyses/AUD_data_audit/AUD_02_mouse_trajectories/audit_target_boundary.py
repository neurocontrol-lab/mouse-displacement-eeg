"""Test provisional target circles against the logged outward reaches."""

from collections import Counter, defaultdict
import csv
import gzip

import numpy as np

from audit_mouse_trajectories import (
    lateral_speed, outward_reach, read_csv, read_trials, result_path, save_csv,
    staged_outputs, target_segment_end,
)


LABEL_RADIUS_PX = 40
RADII_PX = (30, LABEL_RADIUS_PX, 50)
COMPLETE_ENTRY = {"return_detected", "nominal_deadline", "target_changed"}


def assess(trial, row):
    time, x, y = trial.samples.T
    anchor = trial.jump if trial.jump is not None else trial.movement
    outward = outward_reach(trial, lateral_speed(trial))
    last, observation_end = target_segment_end(trial, anchor)
    target_x, target_y = trial.final_target
    distances = np.hypot(x - target_x, y - target_y)
    assert (target_x, target_y) == (float(row["final_target_x_px"]), float(row["final_target_y_px"]))
    assert outward.reason == row["outward_end_reason"]
    assert outward.end <= last and anchor <= outward.closest <= outward.end
    assert round(distances[outward.end], 3) == float(row["outward_end_distance_px"])
    assert round(distances[outward.closest], 3) == float(row["closest_distance_px"])

    identity = {key: row[key] for key in ("run", "trial", "subject", "session", "condition")}
    hits = np.flatnonzero(distances[anchor:last + 1] <= LABEL_RADIUS_PX)
    first_hit = anchor + int(hits[0]) if hits.size else None
    label = dict(
        **identity, radius_px=LABEL_RADIUS_PX,
        outcome="hit_detected" if first_hit is not None else "no_hit_detected",
        first_hit_ms_from_anchor=round((time[first_hit] - time[anchor]) * 1000, 3) if first_hit is not None else None,
        observed_through_ms_from_anchor=round((time[last] - time[anchor]) * 1000, 3),
        observation_end_reason=observation_end,
    )

    details = []
    outward_slice = slice(anchor, outward.end + 1)
    consecutive_times = np.diff(time[outward_slice]) > 0
    for radius in RADII_PX:
        inside = distances[outward_slice] <= radius
        entered = np.flatnonzero(inside)
        first = anchor + int(entered[0]) if entered.size else None
        pair_entry = bool(np.any(inside[:-1] & inside[1:] & consecutive_times))
        endpoint = "indeterminate"
        if outward.reason == "return_detected":
            endpoint = "hit" if inside[-1] else "miss"
        entry = "hit" if first is not None else (
            "miss" if outward.reason in COMPLETE_ENTRY else "indeterminate"
        )
        later = None
        if outward.reason == "return_detected" and first is None:
            later_entries = np.flatnonzero(distances[outward.end + 1:last + 1] <= radius)
            if later_entries.size:
                later = outward.end + 1 + int(later_entries[0])
        details.append(dict(
            **identity, manuscript_label=row["manuscript_label"],
            radius_px=radius, outward_end_reason=outward.reason, endpoint=endpoint, entry=entry,
            two_sample_entry=int(pair_entry),
            end_y_from_target_px=round(y[outward.end] - target_y, 3),
            first_entry_ms_from_anchor=round((time[first] - time[anchor]) * 1000, 3) if first is not None else None,
            first_entry_ms_after_estimated_end=round((time[later] - time[outward.end]) * 1000, 3) if later is not None else None,
            later_entry_y_change_px=round(y[later] - y[outward.end], 3) if later is not None else None,
        ))
    return label, details


def audit():
    out = result_path("AUD_02")
    with gzip.open(out / "trial_audit.csv.gz", "rt", encoding="utf-8", newline="") as stream:
        source = {(r["run"], r["trial"]): r for r in csv.DictReader(stream) if r["eeg_accepted"] == "1"}
    parsed = result_path("PRE_01") / "parsed"
    labels, records = [], []
    coverage = defaultdict(Counter)
    for recording in read_csv(parsed / "manifest.csv"):
        for trial in read_trials(parsed, recording, include_target_positions=True):
            row = source.pop((recording["run"], trial.metadata["trial"]), None)
            if row is None:
                continue
            label, details = assess(trial, row)
            labels.append(label)
            records.extend(details)
            for record in details:
                for session in ("all", record["session"]):
                    for reason in ("all", record["outward_end_reason"]):
                        key = record["radius_px"], record["condition"], session, reason
                        n = coverage[key]
                        n.update(("trials", "endpoint_" + record["endpoint"], "entry_" + record["entry"]))
                        n["two_sample_hits"] += record["two_sample_entry"]
                        n["entries_after_estimated_end"] += record["first_entry_ms_after_estimated_end"] is not None
    assert not source
    fields = ("trials", "endpoint_hit", "endpoint_miss", "endpoint_indeterminate",
              "entry_hit", "entry_miss", "entry_indeterminate", "two_sample_hits", "entries_after_estimated_end")
    summary = [
        dict(radius_px=radius, condition=condition, session=session, outward_end_reason=reason,
             **{field: counts[field] for field in fields})
        for (radius, condition, session, reason), counts in sorted(coverage.items())
    ]
    with staged_outputs(out / "target_boundary") as work:
        save_csv(work / "observed_hit_trials.csv.gz", labels)
        save_csv(work / "boundary_trials.csv.gz", records)
        save_csv(work / "boundary_counts.csv", summary)
    for (condition, outcome), n in sorted(Counter((r["condition"], r["outcome"]) for r in labels).items()):
        print(f"{condition} {outcome}: {n:,}")


if __name__ == "__main__":
    audit()
