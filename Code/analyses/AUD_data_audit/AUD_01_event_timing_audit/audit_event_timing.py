
"""Audit recorded movement and target-jump timing and infer candidate crossings."""

from collections import defaultdict
from contextlib import contextmanager
import csv
from dataclasses import dataclass
import gzip
from io import TextIOWrapper
import json
from pathlib import Path
from shutil import copyfile
import sys
from tempfile import TemporaryDirectory

import numpy as np

sys.path.insert(0, str(next(p for p in Path(__file__).resolve().parents if p.name == "Code")))
from research_paths import ROOT, result_path


MARKERS = {400: "movement", 500: "jump"}
EEG_MS_PER_SAMPLE = 2
CURSOR_PX_PER_MOUSE_MM = 6  # Nominal protocol scale: 1,200 px per 200 mm.
SEARCH_MS = 1250
MARGIN_MS = 6
MIN_RUN_TRIALS = 4
FORWARD_STEP = "forward_step_px"
STEP_2D = "step_2d_px"
FORWARD_SPEED = "forward_speed_mm_s"
SPEED_2D = "speed_2d_mm_s"


@dataclass
class Trial:
    metadata: dict
    samples: np.ndarray  # Mouse log columns: time in seconds, x and y in cursor pixels.
    movement: int
    jump: int | None
    initial_target: tuple[int, int]
    final_target: tuple[int, int]
    target_positions: np.ndarray | None = None

    def observed_index(self, marker):
        return self.movement if marker == 400 else self.jump


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        yield from csv.DictReader(stream)


@contextmanager
def csv_output(path, fields):
    if path.suffix == ".gz":
        with path.open("wb") as raw, gzip.GzipFile(fileobj=raw, filename="", mode="wb", mtime=0) as packed:
            with TextIOWrapper(packed, encoding="utf-8", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(fields)
                yield writer
    else:
        with path.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(fields)
            yield writer


@contextmanager
def staged_outputs(out):
    """Build all outputs before publishing files with the destination permissions."""
    out.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=out) as temporary:
        work = Path(temporary)
        yield work
        # Create siblings under the destination ACL before replacing the saved files.
        # A rename out of the private temporary directory retains its ACL on Windows.
        for path in work.iterdir():
            staged = out / f".{work.name}-{path.name}"
            try:
                copyfile(path, staged)
                staged.replace(out / path.name)
            finally:
                staged.unlink(missing_ok=True)


def read_trials(parsed, recording, include_target_positions=False):
    """Join PRE_01 trial IDs to the same usable mouse log as the event parser."""
    run = recording["run"]
    by_mouse_trial = {
        int(row["mouseTrial"]): row for row in read_csv(parsed / f"{run}_trials.csv")
        if row["valid"] == "1"
    }
    if not by_mouse_trial:
        return []
    pattern = f"{run[:8]}*{run[14:-4]}_tdcserror_.csv"
    logs = [
        log for log in (ROOT / "data" / recording["subject"]).glob(pattern)
        if any(row["event"] == "100" for row in read_csv(log))
    ]
    if len(logs) != 1:
        raise ValueError(f"{run}: expected one usable mouse log, found {len(logs)}")

    samples, movements, jumps, targets = {}, {}, {}, {}
    target_positions = defaultdict(list) if include_target_positions else None
    with logs[0].open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.reader(stream)
        assert next(reader) == ["trial", "time", "x", "y", "z", "x_target", "y_target", "z_target", "event"]
        for row in reader:
            if not row:
                continue
            tid = int(row[0])
            if tid not in by_mouse_trial:
                continue
            time = float(row[1])
            event = row[8]
            if event == "300":
                assert tid not in samples, (run, tid, event)
                samples[tid] = []
                targets[tid] = [(int(row[5]), int(row[6]))]
            if tid not in samples:
                continue
            points = samples[tid]
            if points and (time - points[0][0])*1000 > SEARCH_MS:
                continue
            if event == "400":
                assert tid not in movements, (run, tid, event)
                movements[tid] = len(points)
            if event == "500":
                assert tid not in jumps, (run, tid, event)
                start_x, start_y = targets[tid][0]
                assert int(row[5]) - start_x == int(by_mouse_trial[tid]["mouseJump"])
                assert int(row[6]) == start_y
                targets[tid].append((int(row[5]), int(row[6])))
                jumps[tid] = len(points)
            points.append((time, float(row[2]), float(row[3])))
            if target_positions is not None:
                target_positions[tid].append([float(value) if value else np.nan for value in row[5:7]])

    trials = []
    for tid, metadata in sorted(by_mouse_trial.items(), key=lambda item: int(item[1]["trial"])):
        move, jump = movements.get(tid), jumps.get(tid)
        if move is None or (metadata["label"] == "2") != (jump is not None):
            raise ValueError(f"{run} trial {tid}: a validated marker is missing inside the search window")
        assert move > 0 and (jump is None or jump > move), (run, tid, move, jump)
        points = np.array(samples[tid], dtype=float)
        assert np.isfinite(points).all() and np.all(np.diff(points[:, 0]) >= 0), (run, tid)
        positions = np.array(target_positions[tid]) if target_positions is not None else None
        trials.append(Trial(metadata, points, move, jump, targets[tid][0], targets[tid][-1], positions))
    return trials


def signals(trial, marker):
    """Return named threshold signals in the native cursor or nominal mouse units."""
    time, x, y = trial.samples.T
    dt = np.diff(time, prepend=np.nan)
    dx = np.diff(x, prepend=x[0])
    dy = -np.diff(y, prepend=y[0])
    step = np.hypot(dx, dy)
    vy = np.divide(dy, CURSOR_PX_PER_MOUSE_MM * dt, out=np.full_like(dy, np.nan), where=dt > 0)
    speed = np.divide(step, CURSOR_PX_PER_MOUSE_MM * dt, out=np.full_like(dy, np.nan), where=dt > 0)
    ay = np.divide(np.diff(vy, prepend=np.nan), dt, out=np.full_like(dy, np.nan), where=dt > 0)
    path = np.cumsum(step)
    features = {
        FORWARD_STEP: dy,
        STEP_2D: step,
        FORWARD_SPEED: vy,
        SPEED_2D: speed,
        "forward_acceleration_mm_s2": ay,
        "forward_step_change_px": np.diff(dy, prepend=np.nan),
        "forward_position_px": -y,
    }
    anchors = {"target": 0}
    if marker == 500:
        anchors["movement"] = trial.movement
    for anchor, index in anchors.items():
        features[f"forward_from_{anchor}_px"] = y[index] - y
        features[f"straight_from_{anchor}_px"] = np.hypot(x-x[index], y-y[index])
        features[f"path_from_{anchor}_px"] = path - path[index]
        features[f"elapsed_from_{anchor}_ms"] = (time - time[index])*1000
    return features


def fit_bounds(trial, marker, features):
    """An exact first crossing occurs for prior maximum < cutoff <= observed value."""
    start = 1 if marker == 400 else trial.movement
    observed = trial.observed_index(marker)
    bounds = []
    for values in features.values():
        before = values[start:observed]
        finite = before[np.isfinite(before)]
        bounds.append((finite.max() if finite.size else -np.inf, values[observed]))
    return bounds


def choose_cutoffs(bounds):
    """Maximize exact first-crossing matches on training trials, taking the lowest tie."""
    cutoffs = []
    for intervals in bounds.transpose(1, 0, 2):
        lower, upper = intervals.T
        valid = (lower < upper) & np.isfinite(upper)
        if not valid.any():
            cutoffs.append(np.nan)
            continue
        lower, upper = np.sort(lower[valid]), np.sort(upper[valid])
        candidates = np.unique(upper)
        hits = np.searchsorted(lower, candidates, side="left") - np.searchsorted(upper, candidates, side="left")
        cutoffs.append(candidates[hits.argmax()])
    return cutoffs


@dataclass
class Scores:
    trials: int = 0
    predicted: int = 0
    exact: int = 0
    within_6ms: int = 0
    within_one_sample: int = 0
    signed_ms: float = 0.0
    absolute_ms: float = 0.0

    def add(self, samples, ms):
        self.trials += 1
        if samples is None:
            return
        self.predicted += 1
        self.exact += samples == 0
        self.within_6ms += abs(ms) <= MARGIN_MS
        self.within_one_sample += abs(samples) <= 1
        self.signed_ms += ms
        self.absolute_ms += abs(ms)

    def row(self):
        return [
            self.trials, self.predicted, self.exact, self.within_6ms, self.within_one_sample,
            *[round(100*n/self.trials, 4) for n in (self.exact, self.within_6ms, self.within_one_sample)],
            round(self.signed_ms/self.predicted, 4) if self.predicted else "",
            round(self.absolute_ms/self.predicted, 4) if self.predicted else "",
        ]


def fixed_rules(marker):
    if marker == 400:
        return {
            "forward_50_mm_s": (FORWARD_SPEED, 50),
            "2d_50_mm_s": (SPEED_2D, 50),
            "forward_3_px": (FORWARD_STEP, 3),
            "2d_3_px": (STEP_2D, 3),
        }
    # Exploratory jump references from the earlier audit of these recordings.
    return {
        "forward_18_px": (FORWARD_STEP, 18),
        "forward_560_mm_s": (FORWARD_SPEED, 560),
        "elapsed_84_ms": ("elapsed_from_movement_ms", 84),
    }


def save_observed(out, recordings):
    fields = ["run", "subject", "session", "trial", "mouse_trial", "label",
              "target_eeg_sample", "movement_eeg_sample", "jump_eeg_sample",
              "target_mouse_s", "movement_mouse_s", "jump_mouse_s",
              "movement_eeg_ms_from_target", "movement_mouse_ms_from_target",
              "jump_eeg_ms_from_movement", "jump_mouse_ms_from_movement"]
    measures = (FORWARD_STEP, STEP_2D, FORWARD_SPEED, SPEED_2D)
    fields += [f"{marker}_{measure}" for marker in MARKERS.values() for measure in measures]
    stats = defaultdict(list)
    with csv_output(out / "observed_onsets.csv.gz", fields) as writer:
        for run, trials in recordings.items():
            for trial in trials:
                meta = trial.metadata
                t = trial.samples[:, 0]
                target_eeg, move_eeg = int(meta["targetSample"]), int(meta["movementSample"])
                rt_eeg = (move_eeg-target_eeg)*EEG_MS_PER_SAMPLE
                rt_mouse = (t[trial.movement]-t[0])*1000
                values = {"movement_eeg_ms_from_target": rt_eeg, "movement_mouse_ms_from_target": rt_mouse,
                          "movement_mouse_minus_eeg_ms": rt_mouse-rt_eeg}
                jump_eeg = jump_time = delay_eeg = delay_mouse = ""
                if trial.jump is not None:
                    jump_eeg = int(meta["displacementSample"])
                    jump_time = t[trial.jump]
                    delay_eeg = (jump_eeg-move_eeg)*EEG_MS_PER_SAMPLE
                    delay_mouse = (jump_time-t[trial.movement])*1000
                    values.update(jump_eeg_ms_from_movement=delay_eeg, jump_mouse_ms_from_movement=delay_mouse,
                                  jump_mouse_minus_eeg_ms=delay_mouse-delay_eeg)
                for metric, value in values.items():
                    stats["all", metric].append(value)
                    stats[meta["subject"], metric].append(value)
                features = signals(trial, 400)
                marker_values = [
                    round(features[measure][index], 6) if index is not None else ""
                    for index in (trial.movement, trial.jump) for measure in measures
                ]
                writer.writerow([run, meta["subject"], meta["session"], meta["trial"], meta["mouseTrial"],
                                 meta["label"], target_eeg, move_eeg, jump_eeg, t[0], t[trial.movement],
                                 jump_time, rt_eeg, round(rt_mouse, 6), delay_eeg,
                                 round(delay_mouse, 6) if trial.jump is not None else "", *marker_values])
    with csv_output(out / "marker_timing.csv", ["subject", "metric", "n", "min_ms", "p05_ms",
                                                    "median_ms", "p95_ms", "max_ms"]) as writer:
        for (subject, metric), values in sorted(stats.items()):
            writer.writerow([subject, metric, len(values), *np.percentile(values, [0, 5, 50, 95, 100]).round(4)])


def score_marker(marker, recordings, predictions, cutoffs, cohort, participants):
    # Split chronologically ordered trial IDs within each recording and marker.
    eligible = {}
    for run, trials in recordings.items():
        usable = [trial for trial in trials if trial.observed_index(marker) is not None]
        if len(usable) >= MIN_RUN_TRIALS:
            eligible[run] = usable
    bounds = {}
    for run, trials in eligible.items():
        named = [signals(trial, marker) for trial in trials]
        names = list(named[0])
        bounds[run] = np.array([fit_bounds(t, marker, f) for t, f in zip(trials, named)])
    shared = {}
    for held_out in (0, 1):
        train = np.concatenate([values[1-held_out::2] for values in bounds.values()])
        shared[held_out] = dict(zip(names, choose_cutoffs(train)))
        cutoffs.writerows((marker, "shared", "", held_out, name, value, len(train))
                          for name, value in shared[held_out].items())
    benchmarks = fixed_rules(marker)
    for run, trials in eligible.items():
        for held_out in (0, 1):
            train = bounds[run][1-held_out::2]
            local = dict(zip(names, choose_cutoffs(train)))
            cutoffs.writerows((marker, "per_run", run, held_out, name, value, len(train))
                              for name, value in local.items())
            for trial in trials[held_out::2]:
                time = trial.samples[:, 0]
                observed = trial.observed_index(marker)
                start = 1 if marker == 400 else trial.movement
                features = signals(trial, marker)
                rules = [
                    (scope, name, start, features[name], cutoff)
                    for scope, fit in (("shared", shared[held_out]), ("per_run", local))
                    for name, cutoff in fit.items()
                ]
                rules.extend(("fixed", name, start, features[measure], cutoff)
                             for name, (measure, cutoff) in benchmarks.items())
                for scope, name, first_sample, values, cutoff in rules:
                    crossings = np.flatnonzero(values[first_sample:] >= cutoff)
                    index = int(crossings[0])+first_sample if crossings.size else None
                    samples = index-observed if index is not None else None
                    error = (time[index]-time[observed])*1000 if index is not None else None
                    predictions.writerow([
                        run, trial.metadata["trial"], marker, scope, name, held_out, cutoff,
                        time[index] if index is not None else "",
                        round(error, 6) if error is not None else "", samples if samples is not None else "",
                    ])
                    key = (marker, scope, name)
                    cohort[key].add(samples, error)
                    participants[trial.metadata["subject"], *key].add(samples, error)
    print(f"Marker {marker}: {sum(map(len, eligible.values())):,} held-out trials in {len(eligible)} runs")


def audit():
    parsed = result_path("PRE_01") / "parsed"
    out = result_path("AUD_01")
    recordings = {}
    for number, recording in enumerate(read_csv(parsed / "manifest.csv"), 1):
        trials = read_trials(parsed, recording)
        if trials:
            recordings[recording["run"]] = trials
        if number % 100 == 0:
            print(f"Checked {number} recordings", flush=True)
    print(f"Observed {sum(map(len, recordings.values())):,} movements and "
          f"{sum(t.jump is not None for run in recordings.values() for t in run):,} jumps", flush=True)

    with staged_outputs(out) as work:
        save_observed(work, recordings)
        cohort, participants = defaultdict(Scores), defaultdict(Scores)
        fields = ["run", "trial", "marker", "fit_scope", "candidate", "test_fold", "cutoff",
                  "predicted_mouse_s", "signed_error_ms", "signed_error_samples"]
        fit_fields = ["marker", "fit_scope", "run", "test_fold", "candidate", "cutoff", "training_trials"]
        with csv_output(work / "predicted_onsets.csv.gz", fields) as predictions, \
             csv_output(work / "fitted_cutoffs.csv.gz", fit_fields) as cutoffs:
            for marker in MARKERS:
                score_marker(marker, recordings, predictions, cutoffs, cohort, participants)
        score_fields = ["trials", "predicted", "exact", "within_6ms", "within_one_sample",
                        "exact_pct", "within_6ms_pct", "within_one_sample_pct",
                        "mean_signed_error_ms", "mean_absolute_error_ms"]
        ids = ["marker", "fit_scope", "candidate"]
        with csv_output(work / "threshold_comparison.csv", ids + score_fields) as writer:
            writer.writerows([*key, *scores.row()] for key, scores in sorted(cohort.items()))
        with csv_output(work / "threshold_comparison_by_participant.csv", ["subject", *ids, *score_fields]) as writer:
            writer.writerows([*key, *scores.row()] for key, scores in sorted(participants.items()))
        settings = {
            "markers": MARKERS,
            "nominal_cursor_pixels_per_mouse_mm": CURSOR_PX_PER_MOUSE_MM,
            "eeg_ms_per_sample": EEG_MS_PER_SAMPLE,
            "search_ms_from_initial_target": SEARCH_MS,
            "timing_margin_ms": MARGIN_MS,
            "minimum_trials_per_run_and_marker": MIN_RUN_TRIALS,
            "folds": "Alternate ordered trial IDs within each recording and marker. Fold 0 starts with the first trial.",
            "search_start": "After marker 300 for movement, at marker 400 for jump.",
            "fit": "Maximize exact first crossings in training. Choose the lowest cutoff in a tie.",
            "fixed": {marker: fixed_rules(marker) for marker in MARKERS},
        }
        (work / "settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8")



if __name__ == "__main__":
    audit()
