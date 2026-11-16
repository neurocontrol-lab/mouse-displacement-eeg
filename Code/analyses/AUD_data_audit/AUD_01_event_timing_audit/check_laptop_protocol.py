"""Check the shared laptop protocol's speed thresholds against the study mouse logs."""

from collections import defaultdict

import numpy as np

from audit_event_timing import SCORE_FIELDS, Scores, csv_output, read_csv, read_trials, result_path, staged_outputs


SPEED_READY_PX_MS = 0.5
SPEED_JUMP_PX_MS = 1.5


def first_crossing(speed, threshold, start):
    crossings = np.flatnonzero(speed[start:] > threshold)
    return int(crossings[0]) + start if crossings.size else None


def main():
    parsed = result_path("PRE_01") / "parsed"
    out = result_path("AUD_01")
    summaries = defaultdict(Scores)
    errors = defaultdict(list)

    for number, recording in enumerate(read_csv(parsed / "manifest.csv"), 1):
        subject, run = recording["subject"], recording["run"]
        groups = (("cohort", "", ""), ("participant", subject, ""), ("run", subject, run))
        for trial in read_trials(parsed, recording):
            time, x, y = trial.samples.T
            time_ms = time * 1000
            step = np.hypot(np.diff(x, prepend=x[0]), np.diff(y, prepend=y[0]))
            for clock, ticks in (("logged_intervals", time_ms), ("rounded_ms_intervals", np.rint(time_ms))):
                dt = np.diff(ticks, prepend=np.nan)
                speed = np.divide(step, dt, out=np.full_like(step, np.nan), where=dt > 0)
                rules = [(400, SPEED_READY_PX_MS, 1, trial.movement)]
                if trial.jump is not None:
                    # The onset frame handles state 3. The jump is checked in state 4.
                    rules.append((500, SPEED_JUMP_PX_MS, trial.movement + 1, trial.jump))
                for marker, threshold, start, observed in rules:
                    predicted = first_crossing(speed, threshold, start)
                    sample_error = predicted - observed if predicted is not None else None
                    time_error = round(time_ms[predicted] - time_ms[observed], 6) if predicted is not None else None
                    for group in groups:
                        key = (*group, marker, clock, threshold)
                        summaries[key].add(sample_error, time_error)
                        if time_error is not None:
                            errors[key].append(time_error)
        if number % 100 == 0:
            print(f"Checked {number} recordings", flush=True)

    error_fields = ["early", "late", "median_signed_error_ms"]
    ids = ["scope", "subject", "run", "marker", "clock", "threshold_px_per_ms"]
    with staged_outputs(out) as work:
        with csv_output(work / "laptop_protocol_replay.csv", ids + SCORE_FIELDS + error_fields) as writer:
            for key, scores in sorted(summaries.items()):
                signed = np.asarray(errors[key])
                timing = [int((signed < 0).sum()), int((signed > 0).sum()),
                          round(float(np.median(signed)), 4) if signed.size else ""]
                row = scores.row()
                writer.writerow([*key, *row, *timing])
                if key[0] == "cohort":
                    print(f"{key[3]} {key[4]}: {scores.exact:,}/{scores.trials:,} exact, "
                          f"{scores.within_one_sample:,} within one sample, "
                          f"{scores.within_two_samples:,} within two samples, {timing[2]} ms median error")


if __name__ == "__main__":
    main()
