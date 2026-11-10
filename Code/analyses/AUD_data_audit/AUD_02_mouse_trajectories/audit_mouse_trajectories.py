"""Join behavioural labels to logged reaches and audit endpoints and steering."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import csv
import gzip
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from research_paths import ROOT, code_path, result_path

sys.path.insert(0, str(code_path("AUD_01")))
from audit_event_timing import CURSOR_PX_PER_MOUSE_MM, csv_output, read_csv, read_trials, staged_outputs


SESSIONS = {"1PRE": "pre", "2POST": "post", "3RETEST": "retest"}
SIDE = {"left": -1, "right": 1}
SMOOTH_SECONDS = .030
SUSTAIN_SECONDS = .020
STEER_MM_S = 150
END_TIME_TOLERANCE_MS = 1
END_POSITION_TOLERANCE_PX = .01
WINDOW_SECONDS = .250
TARGET_DURATION_SECONDS = 1
MAX_MOUSE_GAP_SECONDS = .020
RETURN_MM_S = 50
RETURN_SUSTAIN_SECONDS = .030
RETURN_STEP_PX = 20


@dataclass
class OutwardReach:
    end: int
    closest: int
    reason: str
    steering: int | None
    window_status: str


def manuscript_rows():
    table = defaultdict(dict)
    for row in read_csv(ROOT / "data" / "error_correction_25subj_updated.csv"):
        key = (SESSIONS[row["session"]], int(row["block"]), int(row["trial"]))
        trials = table[int(row["subj"])]
        if key in trials:
            raise ValueError(f"Duplicate behavioural table key: {row['subj']}/{key}")
        row["direction"] = SIDE[row["side"]] if row["jump"] == "yes" else 0
        trials[key] = row
    return table


def infer_participant_ids(parsed, manifest, table):
    """Check the 3-state no/left/right displacement sequence across runs."""
    observed = defaultdict(list)
    for rec in manifest:
        for trial in read_csv(parsed / f"{rec['run']}_trials.csv"):
            if trial["valid"] == "1":
                key = rec["session"], int(rec["runNumber"]), int(trial["mouseTrial"])
                observed[rec["subject"]].append((key, int(trial["mouseJump"])//400))
    mapping = {}
    evidence = []
    for subject, trials in sorted(observed.items()):
        scores = []
        for ident, rows in table.items():
            matched = [(direction, rows[key]["direction"]) for key, direction in trials if key in rows]
            n = len(matched)
            correct = sum(a == b for a, b in matched)
            scores.append((correct/n if n else 0, correct, n, ident))
        best, runner_up = sorted(scores, reverse=True)[:2]
        agree, correct, n, ident = best
        if n < .95*len(trials) or agree < .95 or agree-runner_up[0] < .05 or ident in mapping.values():
            raise ValueError(f"{subject}: no unique behavioural ID supported by the displacement sequence")
        mapping[subject] = ident
        evidence.append(dict(subject=subject, manuscript_id=ident, event_valid=len(trials), compared=n,
                             agreement=correct, mismatches=n-correct, agreement_fraction=round(agree, 6),
                             runner_up_fraction=round(runner_up[0], 6)))
    return mapping, evidence


def verified_endpoint(trial, row):
    """Check that target time + manuscript RT + MT locates its reported cursor endpoint."""
    if row is None:
        return None, "behaviour_unlinked", None, None
    fields = ("rt", "mt", "endpointx", "endpointy")
    if any(row[name] in ("", "NA") for name in fields):
        return None, "manuscript_missing", None, None
    rt, mt, end_x, end_y = (float(row[name]) for name in fields)
    time, x, y = trial.samples.T
    end_time = time[0] + (rt + mt)/1000
    index = int(np.argmin(abs(time-end_time)))
    time_error = (time[index]-end_time)*1000
    position_error = np.hypot(x[index]-end_x, y[index]-end_y)
    last_marker = trial.jump if trial.jump is not None else trial.movement
    verified = (index > last_marker and abs(time_error) <= END_TIME_TOLERANCE_MS
                and position_error <= END_POSITION_TOLERANCE_PX)
    return (index if verified else None), ("verified" if verified else "sample_disagreement"), time_error, position_error


def lateral_speed(trial):
    """Estimate lateral mouse speed from a trailing 30 ms cursor interval."""
    time, x, _ = trial.samples.T
    earlier = time - SMOOTH_SECONDS
    sign = np.sign(int(trial.metadata["mouseJump"])) if trial.jump is not None else 1
    speed = sign*(x - np.interp(earlier, time, x))/(CURSOR_PX_PER_MOUSE_MM*SMOOTH_SECONDS)
    speed[earlier < time[0]] = np.nan
    return speed


def adjustment(trial, end, speed):
    if trial.jump is None:
        return "not_applicable", None
    if end is None:
        return "endpoint_unavailable", None
    time = trial.samples[:, 0]
    start = int(np.searchsorted(time, time[trial.jump]+SMOOTH_SECONDS))
    if start >= end or time[end]-time[start] < SUSTAIN_SECONDS:
        return "too_short", None
    above = np.flatnonzero(speed[start:end+1] >= STEER_MM_S) + start
    segments = np.split(above, np.flatnonzero(np.diff(above) != 1)+1)
    for indices in segments:
        if len(indices) and time[indices[-1]]-time[indices[0]] >= SUSTAIN_SECONDS:
            if indices[0] == start:
                return "above_at_window_start", None
            return "detected", int(indices[0])
    return "not_detected", None


def target_segment_end(trial, anchor):
    time = trial.samples[:, 0]
    limit = int(np.searchsorted(time, time[0]+TARGET_DURATION_SECONDS, side="right"))-1
    end = max(anchor, limit)
    reason = "nominal_deadline" if limit < len(time)-1 else "log_ended"
    active = np.all(trial.target_positions == trial.final_target, axis=1)
    changes = np.flatnonzero(~active[anchor+1:end+1])
    if changes.size:
        end = anchor+int(changes[0])
        reason = "target_changed"
    gaps = np.flatnonzero(np.diff(time[anchor:end+1]) > MAX_MOUSE_GAP_SECONDS)
    if gaps.size:
        end = anchor+int(gaps[0])
        reason = "log_gap"
    return end, reason


def outward_reach(trial, speed):
    time, x, y = trial.samples.T
    anchor = trial.jump if trial.jump is not None else trial.movement
    end, reason = target_segment_end(trial, anchor)

    # A sustained increase in screen y is motion back toward the starting area.
    backward = (y - np.interp(time-SMOOTH_SECONDS, time, y))/(CURSOR_PX_PER_MOUSE_MM*SMOOTH_SECONDS)
    above = np.flatnonzero(backward[anchor+1:end+1] >= RETURN_MM_S)+anchor+1
    for segment in np.split(above, np.flatnonzero(np.diff(above) != 1)+1):
        if not len(segment):
            continue
        first, last = segment[0], segment[-1]
        if time[last]-time[first] >= RETURN_SUSTAIN_SECONDS and y[last]-y[first] >= RETURN_STEP_PX:
            start = max(anchor, int(np.searchsorted(time, time[first]-SMOOTH_SECONDS)))
            end = start+int(np.argmin(y[start:first+1]))
            reason = "return_detected"
            break

    distance = np.hypot(x[anchor:end+1]-trial.final_target[0], y[anchor:end+1]-trial.final_target[1])
    closest = anchor+int(np.argmin(distance))
    full_status, steering = adjustment(trial, end, speed)
    if trial.jump is None:
        window_status = "not_applicable"
    else:
        deadline = time[trial.jump]+WINDOW_SECONDS
        if time[end] < deadline:
            window_status = "incomplete"
        else:
            last_in_window = int(np.searchsorted(time, deadline, side="right"))-1
            early_status, _ = adjustment(trial, last_in_window, speed)
            window_status = {
                "detected": "early",
                "above_at_window_start": "above_at_window_start",
                "too_short": "incomplete",
                "not_detected": "late" if full_status == "detected" else "not_detected",
            }[early_status]
    return OutwardReach(end, closest, reason, steering, window_status)


def save_csv(path, rows):
    with csv_output(path, list(rows[0])) as writer:
        writer.writerows(row.values() for row in rows)


def rounded(value, digits=3):
    return round(float(value), digits) if value is not None and np.isfinite(value) else None


def example_trace(trial, record, endpoint, outward, *, display_end=None, first_hit=None):
    time, x, y = trial.samples.T
    speed = lateral_speed(trial)
    move, jump = trial.movement, trial.jump
    # Include the pre-movement lead-in and the exact event indices in the displayed path.
    start = int(np.searchsorted(time, time[move]-.100))
    end = max(endpoint, outward.end) if endpoint is not None else outward.end
    if display_end is not None:
        end = display_end
    steering = outward.steering
    selected = set(range(start, end+1, 3))
    selected.update(i for i in (move, jump, steering, endpoint, outward.end, outward.closest, first_hit, end) if i is not None)
    points = [[rounded((time[i]-time[move])*1000), rounded(x[i], 1), rounded(y[i], 1), rounded(speed[i], 1)]
              for i in sorted(selected)]
    trace = dict(
        run=record["run"], trial=int(record["trial"]), points=points,
        initial_target=list(trial.initial_target), final_target=list(trial.final_target),
        movement_xy=[float(x[move]), float(y[move])],
        jump_xy=[float(x[jump]), float(y[jump])] if jump is not None else None,
        steering_xy=[float(x[steering]), float(y[steering])] if steering is not None else None,
        endpoint_xy=[float(x[endpoint]), float(y[endpoint])] if endpoint is not None else None,
        outward_end_xy=[float(x[outward.end]), float(y[outward.end])],
        closest_xy=[float(x[outward.closest]), float(y[outward.closest])],
    )
    if first_hit is not None:
        trace["first_hit_xy"] = [float(x[first_hit]), float(y[first_hit])]
    return trace


def examples_from(groups):
    examples = []
    for group in groups.values():
        with_end = sorted([item for item in group if item[1]["endpoint_distance_px"] is not None],
                          key=lambda item: item[1]["endpoint_distance_px"])
        without_end = [item for item in group if item[1]["endpoint_distance_px"] is None]
        if with_end:
            indices = {round(q*(len(with_end)-1)) for q in (.1, .5, .9)}
            examples.extend(example_trace(*with_end[i]) for i in sorted(indices))
        if without_end:
            examples.append(example_trace(*without_end[len(without_end)//2]))
    return examples


def audit():
    parsed = result_path("PRE_01") / "parsed"
    manifest = list(read_csv(parsed / "manifest.csv"))
    accepted = {(r["run"], int(r["trial"])) for r in read_csv(result_path("DEC_02") / "trial_metadata.csv")}
    table = manuscript_rows()
    mapping, evidence = infer_participant_ids(parsed, manifest, table)
    loaded = []
    used_keys = Counter()
    for number, recording in enumerate(manifest, 1):
        run, subject, session = (recording[k] for k in ("run", "subject", "session"))
        if subject not in mapping:
            continue
        ident = mapping[subject]
        for trial in read_trials(parsed, recording, include_target_positions=True):
            meta = trial.metadata
            key = session, int(recording["runNumber"]), int(meta["mouseTrial"])
            row = table[ident].get(key)
            direction = int(meta["mouseJump"])//400
            if row is not None and row["direction"] == direction:
                used_keys[ident, key] += 1
            loaded.append((run, subject, session, ident, key, trial, row, direction))
        if number % 100 == 0:
            print(f"Checked {number} mouse recordings", flush=True)

    # Check that the shared loader recovers the same set and timestamps as AUD_01.
    with gzip.open(result_path("AUD_01") / "observed_onsets.csv.gz", "rt", encoding="utf-8", newline="") as stream:
        timing = {(r["run"], int(r["trial"])): r for r in csv.DictReader(stream)}
    assert len(timing) == len(loaded)
    trial_rows = []
    groups = defaultdict(list)
    by_session = defaultdict(Counter)
    for run, subject, session, ident, key, trial, row, direction in loaded:
        trial_id = int(trial.metadata["trial"])
        observed = timing[run, trial_id]
        time, x, y = trial.samples.T
        assert float(observed["target_mouse_s"]) == time[0]
        assert float(observed["movement_mouse_s"]) == time[trial.movement]
        assert (float(observed["jump_mouse_s"]) == time[trial.jump]) if trial.jump is not None else not observed["jump_mouse_s"]
        if row is None:
            link = "missing_key"
        elif row["direction"] != direction:
            link = "displacement_disagreement"
        elif used_keys[ident, key] != 1:
            link = "ambiguous_key"
        else:
            link = "linked"
        linked = row if link == "linked" else None
        endpoint, endpoint_status, time_error, position_error = verified_endpoint(trial, linked)
        speed = lateral_speed(trial)
        status, steering = adjustment(trial, endpoint, speed)
        outward = outward_reach(trial, speed)
        distance = np.hypot(x[endpoint]-trial.final_target[0], y[endpoint]-trial.final_target[1]) if endpoint is not None else None
        manuscript_label = (linked["error"] if linked["error"] != "NA" else "not_applicable") if linked else "unlinked"
        is_accepted = (run, trial_id) in accepted
        record = dict(
            run=run, subject=subject, session=session, trial=trial_id, mouse_trial=key[2],
            manuscript_id=ident, condition="D" if direction else "ND", jump_direction=direction,
            behaviour_link=link, manuscript_label=manuscript_label, eeg_accepted=int(is_accepted),
            endpoint_status=endpoint_status, endpoint_time_error_ms=rounded(time_error, 6),
            endpoint_coordinate_error_px=rounded(position_error, 6), endpoint_distance_px=rounded(distance),
            endpoint_mouse_s=float(time[endpoint]) if endpoint is not None else None,
            endpoint_x_px=float(x[endpoint]) if endpoint is not None else None,
            endpoint_y_px=float(y[endpoint]) if endpoint is not None else None,
            final_target_x_px=trial.final_target[0], final_target_y_px=trial.final_target[1],
            endpoint_ms_from_movement=rounded((time[endpoint]-time[trial.movement])*1000) if endpoint is not None else None,
            jump_ms_from_movement=rounded((time[trial.jump]-time[trial.movement])*1000) if trial.jump is not None else None,
            steering_proxy=status,
            steering_ms_from_jump=rounded((time[steering]-time[trial.jump])*1000) if steering is not None else None,
            steering_250=outward.window_status,
            outward_end_reason=outward.reason,
            outward_end_ms_from_movement=rounded((time[outward.end]-time[trial.movement])*1000),
            outward_end_distance_px=rounded(np.hypot(x[outward.end]-trial.final_target[0], y[outward.end]-trial.final_target[1])),
            closest_distance_px=rounded(np.hypot(x[outward.closest]-trial.final_target[0], y[outward.closest]-trial.final_target[1])),
            closest_ms_from_movement=rounded((time[outward.closest]-time[trial.movement])*1000),
            manuscript_endpoint_in_outward=int(endpoint is not None and endpoint <= outward.end),
            outward_steering_ms_from_jump=(
                rounded((time[outward.steering]-time[trial.jump])*1000) if outward.steering is not None else None
            ),
            geometric_outcome="unverified",
        )
        trial_rows.append(record)
        group = subject, session, record["condition"], outward.window_status, is_accepted
        groups[group].append((trial, record, endpoint, outward))
        totals = by_session[subject, session, record["condition"]]
        totals.update(["event_valid", f"behaviour_{link}", f"endpoint_{endpoint_status}", f"steering_{status}",
                       f"steering_250_{outward.window_status}", f"outward_end_{outward.reason}"])
        if is_accepted:
            totals.update(["eeg_accepted", f"eeg_accepted_label_{manuscript_label}"])
            if endpoint is not None:
                totals["eeg_accepted_verified_endpoint"] += 1

    out = result_path("AUD_02")
    columns = sorted({col for summary in by_session.values() for col in summary})
    examples = examples_from(groups)
    with staged_outputs(out) as work:
        save_csv(work / "participant_mapping.csv", evidence)
        save_csv(work / "trial_audit.csv.gz", trial_rows)
        with csv_output(work / "coverage_by_session.csv", ["subject", "session", "condition", *columns]) as writer:
            writer.writerows([*key, *(counts[col] for col in columns)] for key, counts in sorted(by_session.items()))
        (work / "trajectory_examples.json").write_text(
            json.dumps(examples, separators=(",", ":"), allow_nan=False), encoding="utf-8")
    print(f"{len(trial_rows):,} event-valid reaches across {len(mapping)} participants")
    print("Behaviour linkage:", dict(Counter(r["behaviour_link"] for r in trial_rows)))
    print("Endpoints:", dict(Counter(r["endpoint_status"] for r in trial_rows)))
    print("EEG-accepted D, 250 ms labels:", dict(Counter(
        r["steering_250"] for r in trial_rows if r["condition"] == "D" and r["eeg_accepted"]
    )))
    print(f"{len(examples):,} trajectories saved for the interactive report")


if __name__ == "__main__":
    audit()
