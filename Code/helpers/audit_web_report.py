"""Build the portable Data audit report from the saved audit outputs."""

from collections import Counter
import csv
import gzip
import json
from pathlib import Path

from research_paths import ROOT, result_path


CATEGORY = "AUD_data_audit"
STYLE = """
.audit-heading{display:flex;gap:16px;justify-content:space-between;align-items:baseline;flex-wrap:wrap}
.audit-chart{margin:0;min-width:0}
.audit-chart svg{display:block;width:100%;height:auto;color:#53657a;font:11px system-ui,sans-serif}
.audit-chart figcaption{font-weight:600}
.audit-table td:first-child,.audit-table th:first-child{text-align:left}
.audit-table td,.audit-table th{text-align:right}
.audit-table th:first-child{min-width:10em}
.audit-legend{display:flex;gap:10px 18px;flex-wrap:wrap;margin:.5rem 0;font-size:.85rem;color:#53657a}
.audit-legend b{color:#20334b}
#reachTrialField,#reachTrial{max-width:100%;min-width:0}
"""

BODY = """
<p>Use the timing audit to check what the EEG markers represent. Use the trajectory audit to check which behavioural labels and endpoint estimates can be linked to those trials.</p>
<nav aria-label="Audit views"><a href="#timing">Event timing</a><a href="#trajectories">Mouse trajectories</a><a id="targetHitsLink" href="#target-hits" hidden>Observed target hits</a><a href="../../../Code/analyses/AUD_data_audit/README.md">Methods and saved outputs</a><a href="../../../EXPERIMENTS.md">Experiment registry</a></nav>
<section id="timing">
<div class="audit-heading"><h2>AUD_01 · Event timing and target jump</h2><a href="../AUD_01_event_timing_audit/RESULTS.md">Results note</a></div>
<p class="note">Marker 300 is initial target appearance, 400 is movement onset, and 500 is the recorded target jump. Compare observed mouse and EEG intervals, then see how often the candidate thresholds match the mouse marker.</p>
<div class="controls">
<label>Participant<select id="timingSubject"></select></label>
<label>Marker<select id="timingMarker"><option value="500">500 · Target jump</option><option value="400">400 · Movement onset</option></select></label>
<label>Cutoff<select id="timingScope"><option value="per_run">Fitted per run</option><option value="shared">Shared fit</option><option value="fixed">Fixed benchmark</option></select></label>
</div>
<div class="tablewrap"><table id="timingObserved" class="audit-table"></table></div>
<h3>Candidate first crossings</h3>
<p class="note">Fitted cutoffs are evaluated on held-out trials within each recording. The ±6 ms and one-sample columns use different tolerances because log intervals vary slightly.</p>
<p id="timingSharedNote" class="note" hidden>Each fold uses one cutoff across all participants, sessions, and runs. If the fitted values differ, both are shown in fold order. Values are rounded to three decimal places. <a href="../AUD_01_event_timing_audit/fitted_cutoffs.csv.gz">Full-precision cutoffs</a></p>
<p id="timingFixedNote" class="note" hidden></p>
<div class="tablewrap"><table id="timingComparison" class="audit-table"></table></div>
</section>
<section id="trajectories">
<div class="audit-heading"><h2>AUD_02 · Mouse trajectories and reach outcomes</h2><div><a href="../AUD_02_mouse_trajectories/RESULTS.md">Results note</a> · <a href="../../../Code/analyses/AUD_data_audit/README.md#aud_02">Methods</a></div></div>
<p class="note">Compare the verified manuscript endpoint with the closest observed approach to the logged target center during the outward reach. Observed hit records entry into the provisional 40 px circle around the final target center. The 250 ms steering classification describes the cursor motion separately.</p>
<div class="controls">
<label>Participant<select id="reachSubject"></select></label>
<label>Session<select id="reachSession"></select></label>
<label>Displacement<select id="reachCondition"><option value="">All</option><option value="D">Displaced</option><option value="ND">Non-displaced</option></select></label>
<label id="reachHitField" hidden>Observed hit<select id="reachHit"></select></label>
<label>250 ms steering<select id="reachSteering"></select></label>
<label>EEG-accepted only<input type="checkbox" id="reachAccepted"></label>
</div>
<p id="reachSummary" class="note" aria-live="polite"></p>
<div class="tablewrap"><table id="reachCounts" class="audit-table"></table></div>
<h3>Example trajectories</h3>
<p class="note">Observed hit labels cover EEG-accepted trials. Their examples show the full eligible segment, with separate examples for first entry during and after the estimated outward reach when available. Other examples are sampled by endpoint distance. Counts and distances above use all matching trials.</p>
<div class="controls"><label id="reachTrialField">Example trial<select id="reachTrial"></select></label></div>
<p id="reachTrialInfo" aria-live="polite"></p>
<div class="audit-legend"><span><b>Blue</b> cursor</span><span><b>Purple</b> jump and displaced target center</span><span><b>Green</b> manuscript endpoint</span><span><b>Orange</b> detected steering onset</span><span><b>Gray ring</b> estimated outward end</span><span><b>Blue ring</b> closest observed outward approach</span><span id="reachHitLegend" hidden><b>Magenta</b> provisional target circle and first entry</span></div>
<div id="trajectoryCharts" class="grid">
<figure class="card audit-chart"><figcaption>Cursor path and target centers</figcaption><svg id="reachPath" role="img" aria-label="Cursor path with movement, jump, steering, and endpoint positions"></svg></figure>
<figure class="card audit-chart"><figcaption>Endpoint distances in the current selection</figcaption><svg id="reachDistances" role="img" aria-label="Distribution of endpoint distances in cursor pixels"></svg></figure>
<figure class="card audit-chart"><figcaption>Lateral cursor displacement</figcaption><svg id="reachLateral" role="img" aria-label="Cursor lateral displacement over time"></svg></figure>
<figure class="card audit-chart"><figcaption>Lateral mouse speed (nominal)</figcaption><svg id="reachSpeed" role="img" aria-label="Estimated lateral speed over time"></svg></figure>
</div>
<p class="note">Time plots use the jump as zero for displaced trials and movement onset for non-displaced trials. Positive lateral displacement is toward the jump for displaced trials and to the right for non-displaced trials. On displaced trials, the orange dashed line in the speed plot marks the 150 mm/s steering threshold. The orange markers show where and when steering was detected. Early steering requires the threshold to be sustained for 20 ms by 250 ms after the jump. The report labels trials with insufficient outward trajectory coverage separately.</p>
</section>
<section id="target-hits" hidden>
<div class="audit-heading"><h2>AUD_02 · Observed target hits</h2><a href="../AUD_02_mouse_trajectories/target_boundary/RESULTS.md">Results and trial labels</a></div>
<p id="observedHitScope" class="note">Counts cover EEG-accepted trials. A hit is any recorded cursor sample inside or on the provisional 40 px circle, including entry after an overshoot. No hit detected means no entry was recorded before observation ended.</p>
<p id="closeApproachScope" class="note" hidden>Close approach uses the minimum distance to the final target over the full eligible log. The label describes observed proximity.</p>
<div class="controls">
<label>Participant<select id="hitSubject"></select></label>
<label>Session<select id="hitSession"></select></label>
<label id="hitRadiusField" hidden>Threshold<select id="hitRadius">
<option value="40">40 px · Observed hit</option><option value="75">75 px · Close approach</option><option value="100">100 px · Sensitivity</option>
</select></label>
</div>
<div class="tablewrap"><table id="hitCounts" class="audit-table"></table></div>
</section>
<footer>Built from saved AUD_01 and AUD_02 results. The report embeds selected trajectory examples and summary fields. Trial-level audit tables are linked from the methods.</footer>
"""


def rows(path):
    reader = gzip.open if path.suffix == ".gz" else open
    with reader(path, "rt", encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def hit_counts(trials):
    counts = Counter()
    for r in trials:
        key = (r["subject"], r["session"], r["condition"])
        counts[(*key, r["outcome"])] += 1
        for field in ("close_75", "close_100"):
            counts[(*key, field)] += r.get(field) == "1"
    return [
        [*key, *(counts[(*key, field)] for field in ("hit_detected", "no_hit_detected", "close_75", "close_100"))]
        for key in sorted({key[:3] for key in counts})
    ]


def audit_data():
    timing = result_path("AUD_01")
    trajectories = result_path("AUD_02")
    audit = rows(trajectories / "trial_audit.csv.gz")
    index = {(r["run"], int(r["trial"])): r for r in audit}
    boundary = trajectories / "target_boundary"
    hit_file = boundary / "observed_hit_trials.csv.gz"
    hit_labels = {(r["run"], int(r["trial"])): r for r in rows(hit_file)} if hit_file.is_file() else {}
    example_file = boundary / "observed_hit_examples.json"
    hit_examples = json.loads(example_file.read_text(encoding="utf-8")) if example_file.is_file() and hit_labels else []
    examples = json.loads((trajectories / "trajectory_examples.json").read_text(encoding="utf-8"))
    def number(row, field):
        return float(row[field]) if row[field] else None
    def filters(row):
        outcome = hit_labels.get((row["run"], int(row["trial"])), {}).get("outcome", "not_assessed")
        return [
            row["subject"], row["session"], row["condition"], outcome, row["steering_250"],
            int(row["eeg_accepted"]), int(row["behaviour_link"] == "linked"),
            number(row, "endpoint_distance_px"), number(row, "closest_distance_px"),
        ]
    for example in hit_examples:
        label = hit_labels[example["run"], example["trial"]]
        example["hit_radius_px"] = float(label["radius_px"])
        example["first_hit_ms_from_anchor"] = number(label, "first_hit_ms_from_anchor")
        example["full_log_min_distance_px"] = number(label, "full_log_min_distance_px") if "full_log_min_distance_px" in label else None
    if hit_examples:
        # Use full-segment examples where observed hit was assessed.
        examples = hit_examples + [
            example for example in examples if (example["run"], example["trial"]) not in hit_labels
        ]
    for example in examples:
        r = index[example["run"], example["trial"]]
        example["filters"] = filters(r)
        example["jump_direction"] = int(r["jump_direction"])
        for name in ("endpoint_ms_from_movement", "jump_ms_from_movement",
                     "outward_steering_ms_from_jump", "outward_end_ms_from_movement"):
            example[name] = number(r, name)
        example["outward_end_reason"] = r["outward_end_reason"]
    return {
        "subjects": sorted({r["subject"] for r in audit}),
        "timing": rows(timing / "marker_timing.csv"),
        "fixedCutoffs": json.loads((timing / "settings.json").read_text(encoding="utf-8"))["fixed"],
        "sharedCutoffs": [r for r in rows(timing / "fitted_cutoffs.csv.gz") if r["fit_scope"] == "shared"],
        "comparison": rows(timing / "threshold_comparison.csv") + rows(timing / "threshold_comparison_by_participant.csv"),
        "reaches": [filters(row) for row in audit],
        "examples": examples,
        "targetHits": hit_counts(hit_labels.values()),
        "closeApproachAvailable": any("close_75" in label for label in hit_labels.values()),
    }


def build(shared_style, related):
    destination = ROOT / "output" / CATEGORY / "report"
    destination.mkdir(parents=True, exist_ok=True)
    data = json.dumps(audit_data(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    script = Path(__file__).with_name("audit_report.js").read_text(encoding="utf-8")
    page = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<title>Data audit</title><style>{shared_style}{STYLE}</style></head><body>'
        f'<nav aria-label="Research reports">{related}</nav><h1>Data audit</h1>{BODY}'
        f'<script id="audit-data" type="application/json">{data}</script><script>{script}</script></body></html>'
    )
    (destination / "index.html").write_text(page, encoding="utf-8")
    print(f"{CATEGORY}: {len(page)/1e6:.1f} MB HTML")
