
"""ERP-specific content for the shared portable report builder."""

import json

from research_paths import code_path, result_path

CATEGORY = "ERP_event_related_potentials"


def report_spec():
    out = result_path("ERP_01")
    steering = result_path("ERP_02")
    trajectories = result_path("ERP_03")
    outcomes = result_path("ERP_04")
    outcome_titles = {
        "outcome_hit": "Observed hit vs no hit detected",
        "outcome_hit400": "Observed hit by 400 ms",
        "outcome_near75": "Close approach at 75 px",
        "outcome_near100": "Close approach at 100 px",
        "outcome_d_nd_hit": "Displaced vs non-displaced hits",
    }
    return {
        "title": "Event-related potentials",
        "summary": (
            "ERP_01 compares movement- and target-jump-aligned waveforms from the same "
            "displaced (D) and non-displaced (ND) trials. The clearest non-pilot difference "
            "was a positivity near 270 ms after the recorded jump. Only the Cz/FCz "
            "200–280 ms jump window reached the Holm-adjusted threshold. ERP_02 describes "
            "steering and target distance within displaced reaches. ERP_03 compares "
            "the manuscript’s corrective and erroneous trajectories. ERP_04 compares "
            "observed hits and close approaches."
        ),
        "tables": [
            ("Non-pilot group tests", out / "component_tests.csv"),
            ("Participant amplitudes (pooled sessions)", out / "participant_component_amplitudes.csv"),
            ("Participant/session amplitudes", out / "session_component_amplitudes.csv"),
            ("Recording amplitudes", out / "run_component_amplitudes.csv"),
            ("Matched trial coverage", out / "match_coverage.csv"),
            ("ERP_02 steering contrasts", steering / "steering_contrast_summary.csv"),
            ("ERP_02 steering contrasts by participant and session", steering / "steering_contrast_by_session.csv"),
            ("ERP_02 trial coverage", steering / "coverage_by_session.csv"),
            ("ERP_02 distance slope summary", steering / "endpoint_distance_summary.csv"),
            ("ERP_02 distance slopes by participant", steering / "endpoint_distance_slopes.csv"),
            ("ERP_03 trajectory contrast", trajectories / "group_summary.csv"),
            ("ERP_03 trajectory contrast by participant", trajectories / "participant_amplitudes.csv"),
            ("ERP_03 trial coverage", trajectories / "coverage.csv"),
            ("ERP_04 matched-hit window tests (exploratory)", outcomes / "matched_hit_window_tests.csv"),
            ("ERP_04 outcome contrast summary", outcomes / "group_summary.csv"),
            ("ERP_04 outcome contrasts by participant", outcomes / "participant_amplitudes.csv"),
            ("ERP_04 trial coverage", outcomes / "coverage.csv"),
        ],
        "figures": [out / f"{name}.png" for name in (
            "matched_waveforms", "movement_differences_by_session",
            "jump_differences_by_session", "short_vs_long_delay",
        )] + [steering / f"{name}.png" for name in (
            "jump_early_steering", "jump_control_subsets", "jump_and_steering_alignment", "distance_associations",
        )] + [trajectories / "jump_corrective_vs_erroneous.png"] + [outcomes / f"{name}.png" for name in outcome_titles],
        "figure_titles": outcome_titles,
        "figure_descriptions": {
            "outcome_hit": "ERP_04. Jump-aligned displaced trials grouped by entry into the provisional 40 px circle, with pairs matched within recording and jump direction.",
            "outcome_hit400": "ERP_04. Entry by 400 ms after the jump. Both groups have observation through 400 ms.",
            "outcome_near75": "ERP_04. Compare displaced reaches that came within 75 px of the final target with other displaced reaches.",
            "outcome_near100": "ERP_04. Repeat the close-approach comparison at 100 px.",
            "outcome_d_nd_hit": "ERP_04. Compare hits after the logged jump in displaced trials with hits after the matched pseudo-jump in non-displaced trials. See the cohort window tests for the exact Cz/FCz and posterior estimates.",
            "jump_corrective_vs_erroneous": (
                "ERP_03. Corrective and erroneous displaced reaches defined by the manuscript’s "
                "velocity and endpoint-distribution criteria. Pairs share a recording and jump "
                "direction and are matched on reaction time and movement-to-jump delay. "
                "The cohort figure gives each contributing non-pilot participant equal weight."
            ),
            "matched_waveforms": "D, ND and D − ND on eight channels under both alignments. Non-pilot participants have equal weight.",
            "movement_differences_by_session": "Movement-aligned D − ND means for pre, post and retest in the non-pilot group.",
            "jump_differences_by_session": "Jump-aligned D − ND means for pre, post and retest in the non-pilot group.",
            "short_vs_long_delay": (
                "D − ND for the shorter and longer halves of matched pairs within each recording, "
                "ranked by the time from movement onset to the jump on the displaced trial. "
                "Averaged across non-pilot participants."
            ),
            "jump_early_steering": "ERP_02. Early steering versus no early confirmation in matched displaced trials, averaged across non-pilots.",
            "jump_control_subsets": "ERP_02. Early steering minus later steering, and early steering minus no detection, using the corresponding matched pairs.",
            "jump_and_steering_alignment": "ERP_02. Jump- and steering-aligned waveforms on the same trials. The amber band and dashed line mark the other event's 5th–95th percentile range and median.",
            "distance_associations": (
                "Each blue dot is a participant’s fitted change in EEG voltage per 100 px farther from "
                "the target across trials (ΔV/Δdistance). The diamond is the median. A slope farther "
                "from zero means a larger voltage change per 100 px. Negative slopes mean higher "
                "voltage on closer reaches. The primary panel uses the full eligible log, including "
                "late approaches. The other panels use the same trials with outward-only minimum and "
                "manuscript endpoint distances."
            ),
        },
    }


def gallery_windows():
    erp01 = json.loads((code_path("ERP_01") / "windows.json").read_text(encoding="utf-8"))
    options = {}
    for row in erp01:
        name = row["component_window"]
        option = options.setdefault(name, {
            **row, "electrodes": "/".join(row["electrodes"]), "alignments": [],
        })
        option["alignments"].append(row["alignment"])
    extra = (
        ("Target perturbation N100-like", "P3/PO3/PO7", 80, 150, "jump", -1),
        ("Target perturbation P3-like", "P3/PO3/PO7", 200, 400, "jump", 1),
        ("Feedback-related negativity", "Cz/FCz", 200, 300, "feedback", -1),
        ("Feedback P3-like", "CP1/P3", 300, 600, "feedback", 1),
    )
    for name, electrodes, start, end, alignment, sign in extra:
        options[name] = dict(component_window=name, electrodes=electrodes, start_ms=start,
                             end_ms_exclusive=end, alignments=[alignment], expected_sign=sign)
    return list(options.values())


TABLE_LABELS = {
    "alignment": "Alignment", "component_window": "Component window",
    "reference_uv": "Reference (µV)", "comparison_uv": "Comparison (µV)",
    "erroneous_uv": "Erroneous (µV)", "corrective_uv": "Corrective (µV)",
    "difference_uv": "Difference (µV)",
    "mean_difference_uv": "Mean difference (µV)",
    "median_difference_uv": "Median difference (µV)",
    "electrodes": "Electrodes", "start_ms": "Start (ms)", "end_ms_exclusive": "End (ms, exclusive)",
    "expected_sign": "Expected sign (−1/+1)", "participants": "Participants",
    "mean_ND_uV": "Mean ND (µV)", "mean_D_uV": "Mean D (µV)",
    "mean_D_minus_ND_uV": "Mean D − ND (µV)", "ci95_low_uV": "95% CI lower (µV)",
    "ci95_high_uV": "95% CI upper (µV)", "participants_expected_sign": "Participants with expected sign",
    "p": "Raw p", "p_Holm": "Holm-adjusted p", "subject": "Participant",
    "session": "Session", "cohort": "Cohort", "matched_pairs": "Matched pairs",
    "runs": "Usable runs", "run": "Recording", "single_run_sessions": "Sessions with one run",
    "bootstrap95_low_uV": "Run bootstrap 95% lower (µV)",
    "bootstrap95_high_uV": "Run bootstrap 95% upper (µV)",
    "ND_uV": "ND (µV)", "D_uV": "D (µV)", "D_minus_ND_uV": "D − ND (µV)",
    "accepted_ND": "Accepted ND", "accepted_D": "Accepted D",
    "short_pairs": "Short-delay pairs", "long_pairs": "Long-delay pairs",
    "median_absolute_RT_gap_ms": "Median absolute RT gap (ms)",
    "delay_p05_ms": "Jump delay p05 (ms)", "delay_median_ms": "Median jump delay (ms)",
    "delay_p95_ms": "Jump delay p95 (ms)",
}

SCOPE = (
    "The same no-FORCe trial pairs are shown under both alignments. Each pair comes from one recording "
    "and was matched on reaction time. At jump alignment, time zero is the recorded target jump on D "
    "trials and the same delay after movement on the paired ND trials. Both views retain the original "
    "−200 to 0 ms movement baseline. The contrast can include responses to the visual change and "
    "corrective movement as well as error-related activity."
)

TEST_SCOPE = (
    '<p class="note">The eight group tests use the 23 non-pilot participants, all matched pairs '
    'and pooled sessions. The confidence intervals are marginal 95% intervals. Holm adjusts '
    'across all eight tests. The other tables describe individuals.</p>'
)

WAVE_SECTION = """
<section id="erpSection" aria-labelledby="erp-heading">
<h2 id="erp-heading">Explore the matched waveforms</h2>
<div class="controls">
<label>Participant or cohort<select id="erpSubject"></select></label>
<label>Session<select id="erpSession"><option value="all">Pooled sessions</option></select></label>
<label>Alignment<select id="erpAlignment"><option value="jump">Target jump / pseudo-jump</option><option value="movement">Movement onset</option></select></label>
<label>Jump delay group<select id="erpDelay"><option value="0">All matched pairs</option><option value="1">Shorter delays</option><option value="2">Longer delays</option></select></label>
<label>Shade a test window<select id="erpWindow"></select></label>
</div>
<div class="erp-legend" aria-label="Visible waveforms">
<label><input type="checkbox" value="0" checked><span style="color:#1f5a96">Non-displaced</span></label>
<label><input type="checkbox" value="1" checked><span style="color:#aa4834">Displaced</span></label>
<label><input type="checkbox" value="2" checked><span style="color:#27232b">D − ND</span></label>
</div>
<p id="erpCounts" class="note" aria-live="polite"></p>
<p class="note">Pooled sessions weight pairs equally within each participant. Cohort views weight participants equally.
Within each recording, pairs are ranked by the time from movement onset (400) to the target jump (500) on the displaced trial.
The shorter and longer groups contain equal numbers of pairs. An odd middle pair appears only in the full set.
Reaction time from initial target appearance (300) to movement onset (400) is used to match D and ND before this split.
The eight panels share a voltage scale within each selection. The shaded interval marks the test electrodes.</p>
<div id="erpWaves" class="grid"></div>
</section>
"""

REPEATABILITY_SECTION = """
<section aria-labelledby="erp-repeat-heading">
<h2 id="erp-repeat-heading">Repeatability within participants</h2>
<p class="note">Each dot on the left is a pooled participant estimate. Its exploratory 95% interval resamples whole runs
within pre, post and retest, with session weights fixed. The plots use all matched pairs in the selected window.</p>
<div class="controls">
<label>Predefined window<select id="erpRepeatWindow"></select></label>
<label>Participant to inspect<select id="erpRepeatSubject"></select></label>
</div>
<div class="grid">
<figure class="chart"><figcaption>Pooled participant estimates and 95% intervals (* pilot)</figcaption>
<svg id="erpRepeatForest" class="erp-plot" role="img" aria-label="Participant amplitudes and 95% intervals"></svg></figure>
<figure class="chart"><figcaption>Run dots and pair-weighted session means (diamonds)</figcaption>
<svg id="erpRepeatRuns" class="erp-plot" role="img" aria-label="Run and session amplitudes"></svg>
<p id="erpRepeatEstimate" aria-live="polite"></p>
<ul id="erpRepeatSessionList" class="note"></ul></figure>
</div>
<p class="note">Use the session estimates to assess recurrence of sign and size. A session with one usable run
contributes a fixed estimate to the pooled interval. Intervals describe run-to-run uncertainty in the observed
sessions and are marginal across the displayed windows and participants.</p>
</section>
"""

STYLE = """
.grid:has(#erpRepeatForest){align-items:start}
.erp-legend{display:flex;flex-wrap:wrap;gap:18px}
.erp-legend label{flex-direction:row;align-items:center;gap:5px}
.erp-legend span{border-bottom:2px solid currentColor}
.erp-plot{display:block;width:100%;height:auto;color:#53657a;font:11px system-ui,sans-serif}
.erp-supported{background:#e7f2fa;font-weight:600}
#erpTestForest{max-width:850px}
#erpDistanceValues td:nth-child(2){white-space:normal;min-width:12em}
#erpGalleryWindowField{min-width:0;max-width:100%}
.erp-cursor{margin:0;color:#53657a;font:12px system-ui,sans-serif;min-height:1.5em;font-variant-numeric:tabular-nums}
"""


FINDINGS_NAV = """
<nav aria-label="ERP results">
<a href="#erp-window-tests">Cohort window tests</a>
<a href="#erp-distance">Distance associations</a>
<a href="#savedFigures">Waveform gallery</a>
</nav>
"""

FINDINGS_SECTION = """
<section id="erp-window-tests" aria-labelledby="erp-tests-heading">
<h2 id="erp-tests-heading">Cohort window tests</h2>
<p id="erpTestSummary" aria-live="polite"></p>
<div class="controls"><label>Contrast<select id="erpTestContrast"></select></label></div>
<p id="erpTestMethod" class="note"></p>
<p><a href="#savedFigures" id="erpTestWaveform">Open this contrast in the waveform gallery</a></p>
<figure><svg id="erpTestForest" class="erp-plot" role="img" aria-label="Mean differences with marginal 95 percent confidence intervals"></svg>
<figcaption>Each dot is a cohort mean. Bars show marginal 95% intervals. Blue marks indicate Holm-adjusted p &lt; .05. The vertical line marks zero difference. Window names describe the ERP references, and the dots show the measured polarity.</figcaption></figure>
<div class="tablewrap"><table id="erpTestValues"></table></div>
</section>
<section id="erp-distance" aria-labelledby="erp-distance-heading" hidden>
<h2 id="erp-distance-heading">ERP_02 · Distance associations</h2>
<p>The three panels use the same 9,628 displaced trials and the same EEG windows. They differ in where along the mouse trajectory distance is measured. The full-log and outward-only minima are our definitions. The manuscript endpoint is the original estimate from the behavioural analysis.</p>
<figure><img id="erpDistancePlot" alt="Cohort distance slopes for the three target distance definitions">
<figcaption>Blue dots are individual non-pilot slopes. Diamonds mark their median. Farther from zero means a larger voltage change per 100 px. A negative slope means higher voltage on closer reaches.</figcaption></figure>
<div class="tablewrap"><table id="erpDistanceValues"></table></div>
<p class="note">The strongest window in each panel is selected by absolute median slope. These are descriptive slopes.</p>
</section>
"""

GALLERY_WINDOW = """
<label id="erpGalleryWindowField">ERP morphology window<select id="erpGalleryWindow">
<option value="">None</option>
</select></label>
"""

GALLERY_NOTES = """
<p id="erpGalleryWindowNote" class="note" aria-live="polite" hidden></p>
<p id="erpGalleryFindingLink" hidden></p>
<details><summary>ERP windows and event alignment</summary>
<p>The selector shades candidate time ranges at the listed electrodes. The ERN-like and Pe-like overlays are morphology references at movement onset and the jump. The interaction and target-perturbation windows use the jump. The Graz windows use movement onset. Shading identifies the comparison window.</p>
<p>Feedback-related negativity and feedback P3 are listed as references. A verified outcome cue is needed to align these windows. <a href="https://pubmed.ncbi.nlm.nih.gov/23964600/">Feedback negativity study</a> · <a href="https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2012.00029/full">Feedback P3 study</a> · <a href="https://www.krigolsonlab.com/uploads/4/3/8/4/43848243/krigolson_2007_hep.pdf">Target perturbation N100 and P300 study</a></p>
</details>
"""
