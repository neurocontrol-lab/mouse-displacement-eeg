
"""ERP-specific content for the shared portable report builder."""

from research_paths import result_path

CATEGORY = "ERP_event_related_potentials"


def report_spec():
    out = result_path("ERP_01")
    return {
        "title": "Event-related potentials",
        "summary": (
            "ERP_01 compares movement- and target-jump-aligned waveforms from the same "
            "displaced (D) and non-displaced (ND) trials. The clearest non-pilot difference "
            "was a positivity near 270 ms after the recorded jump. Only the Cz/FCz "
            "200–280 ms jump window reached the Holm-adjusted threshold."
        ),
        "tables": [
            ("Non-pilot group tests", out / "component_tests.csv"),
            ("Participant amplitudes (pooled sessions)", out / "participant_component_amplitudes.csv"),
            ("Participant/session amplitudes", out / "session_component_amplitudes.csv"),
            ("Recording amplitudes", out / "run_component_amplitudes.csv"),
            ("Matched trial coverage", out / "match_coverage.csv"),
        ],
        "figures": [out / f"{name}.png" for name in (
            "matched_waveforms", "movement_differences_by_session",
            "jump_differences_by_session", "short_vs_long_delay",
        )],
        "figure_descriptions": {
            "matched_waveforms": "D, ND and D − ND on eight channels under both alignments. Non-pilot participants have equal weight.",
            "movement_differences_by_session": "Movement-aligned D − ND means for pre, post and retest in the non-pilot group.",
            "jump_differences_by_session": "Jump-aligned D − ND means for pre, post and retest in the non-pilot group.",
            "short_vs_long_delay": "D − ND for the shorter and longer halves of the jump delays within each recording, averaged across non-pilot participants.",
        },
    }


TABLE_LABELS = {
    "alignment": "Alignment", "component_window": "Component window",
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
<label>Delay group<select id="erpDelay"><option value="0">All matched pairs</option><option value="1">Shorter delays</option><option value="2">Longer delays</option></select></label>
<label>Shade a test window<select id="erpWindow"></select></label>
</div>
<div class="erp-legend" aria-label="Visible waveforms">
<label><input type="checkbox" value="0" checked><span style="color:#1f5a96">Non-displaced</span></label>
<label><input type="checkbox" value="1" checked><span style="color:#aa4834">Displaced</span></label>
<label><input type="checkbox" value="2" checked><span style="color:#27232b">D − ND</span></label>
</div>
<p id="erpCounts" class="note" aria-live="polite"></p>
<p class="note">Pooled sessions weight pairs equally within each participant. Cohort views weight participants equally.
Shorter and longer delays are ranked within each recording; an odd middle pair appears only in the full set.
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
.erp-cursor{margin:0;color:#53657a;font:12px system-ui,sans-serif;min-height:1.5em;font-variant-numeric:tabular-nums}
"""
