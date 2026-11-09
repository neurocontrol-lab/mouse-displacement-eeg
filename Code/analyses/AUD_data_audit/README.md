# AUD — Data audit

Validate event timing and behavioural labels before they are used to group EEG epochs.

[Experiment registry](../../../EXPERIMENTS.md) · [Interactive report](../../../output/AUD_data_audit/report/index.html)

| ID | Audit | Results |
|---|---|---|
| [AUD_01](#aud_01) | Event timing and target-jump audit | [Results note](../../../output/AUD_data_audit/AUD_01_event_timing_audit/RESULTS.md) |
| [AUD_02](#aud_02) | Mouse trajectories and reach outcomes | [Report](../../../output/AUD_data_audit/report/index.html#trajectories) |

## AUD_01

**Event timing and target-jump audit.** Compare the logged movement onset (400) and target jump (500) in PRE_01 and the corresponding mouse logs. Test candidate trigger rules using the observed marker as the reference.

| Step | Script | Operation |
|---|---|---|
| 1 | [audit_event_timing.py](AUD_01_event_timing_audit/audit_event_timing.py) | Join mouse and EEG markers, fit candidate cutoffs, and export trial predictions and timing summaries. |

Run from the repository root after PRE_01 parsing, with the original mouse logs available.

~~~text
python Code/analyses/AUD_data_audit/AUD_01_event_timing_audit/audit_event_timing.py
~~~

Movement onset uses both displaced and non-displaced trials. Jump onset uses displaced trials. The search starts after initial target appearance (300) for movement and at logged movement onset for the jump. Both searches end at 1.25 s after the initial target or the last available sample in the trial. Fixed benchmarks use the same search start as the fitted rules for each marker. [Graz protocol](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf)

| Candidate | Measure |
|---|---|
| Forward or 2D step | Signed forward y displacement, or magnitude of the x/y displacement between successive samples. Units are cursor pixels per logged sample. |
| Forward or 2D speed | Divide each step by actual elapsed time. Use the nominal scale of six cursor pixels per mm of physical mouse travel to estimate mm/s. |
| Forward acceleration or step change | Difference in successive forward speeds per second, or difference in successive forward steps. |
| Absolute forward position | Negated cursor y coordinate, so movement toward the target increases the measure. |
| Forward, straight-line or cumulative path distance | Distance from initial target appearance. For the jump, also test each measure from logged movement onset. |
| Elapsed time | Time from initial target appearance, or from logged movement onset for the jump. |

For each marker and recording with at least four usable trials, alternate ordered trial IDs into two folds. Fit on one fold and score the other, then swap. Fit a single shared cutoff across the training halves of all eligible recordings and separate cutoffs from each recording's own training half. Choose the cutoff that maximizes exact first crossings in training, breaking ties toward the lower cutoff. The draft describes 50 mm/s for longitudinal movement onset and offset using smoothed positions and 150 mm/s for lateral correction. For marker 400, the audit compares 3 px per sample and 50 mm/s using consecutive log samples in forward and 2D motion. For marker 500, the fixed references are exploratory. They use 18 px per sample from the shared forward step fit, 560 mm/s from the rounded median fitted forward speed, and 84 ms from the observed median delay. All three values were chosen from these recordings. Report exact matches, matches within ±6 ms and matches within one logged sample separately. All rates include trials with no predicted crossing. Signed error is predicted minus observed mouse time.

| Saved output | Contents |
|---|---|
| [Observed onsets](../../../output/AUD_data_audit/AUD_01_event_timing_audit/observed_onsets.csv.gz) | Per-trial EEG sample indices and mouse timestamps for markers 300, 400 and 500, with cursor steps and nominal speeds at 400 and 500. |
| [Marker timing](../../../output/AUD_data_audit/AUD_01_event_timing_audit/marker_timing.csv) | Cohort and participant timing distributions, including mouse-minus-EEG interval differences. |
| [Fitted cutoffs](../../../output/AUD_data_audit/AUD_01_event_timing_audit/fitted_cutoffs.csv.gz) | Cutoff for each marker, candidate and training fold, pooled or by recording. |
| [Predicted onsets](../../../output/AUD_data_audit/AUD_01_event_timing_audit/predicted_onsets.csv.gz) | Held-out predicted crossing, applied cutoff and signed error in ms and logged samples. |
| [Cohort comparison](../../../output/AUD_data_audit/AUD_01_event_timing_audit/threshold_comparison.csv) and [participant comparison](../../../output/AUD_data_audit/AUD_01_event_timing_audit/threshold_comparison_by_participant.csv) | Match rates, prediction counts and errors conditional on a crossing. |

The [results note](../../../output/AUD_data_audit/AUD_01_event_timing_audit/RESULTS.md) summarises the marker timing, the strongest candidate rules, and the limits of the inference. [ERP_01](../ERP_event_related_potentials/README.md#erp_01) uses the logged event times for alignment.

## AUD_02

**Mouse trajectories and reach outcomes.** Join the behavioural table to event-valid reaches and inspect the cursor at movement onset, target jump and the manuscript's estimated movement endpoint.

| Step | Script | Operation |
|---|---|---|
| 1 | [audit_mouse_trajectories.py](AUD_02_mouse_trajectories/audit_mouse_trajectories.py) | Verify the join and manuscript endpoints, measure follow-through, classify steering, and save trajectory examples and coverage. |
| 2 | [build_web_reports.py](../../helpers/build_web_reports.py) | Build the combined AUD_01 and AUD_02 interactive report. |

Run from the repository root with the original mouse logs, the supplied behavioural CSV, PRE_01 parsed trials, AUD_01 observed markers and the DEC_02 trial selection available.

~~~text
python Code/analyses/AUD_data_audit/AUD_02_mouse_trajectories/audit_mouse_trajectories.py
python Code/helpers/build_web_reports.py --category AUD_data_audit
~~~

The behavioural table has numeric participant IDs. Infer the mapping from no-jump, left-jump and right-jump sequences using session, block and mouse trial number. Check for a unique mapping and require the displacement condition and direction to agree on each joined row. The manuscript's labels combine lateral velocity and endpoint distributions. Store them separately from the trajectory proxy and endpoint distance.

**Endpoint.** Add the supplied reaction time and movement duration to the initial target timestamp to locate the proposed endpoint. Require a raw cursor sample after the last task marker within 1 ms and 0.01 px of the supplied time and coordinates. Measure the verified sample's Euclidean distance from the final logged target center. Target geometry and a timed outcome cue are unverified, so geometric hit/miss remains unclassified.

**Manuscript-end steering proxy.** For displaced trials, orient lateral velocity toward the jump and estimate it from the trailing 30 ms of cursor movement at the nominal 6 px/mm scale. Search from 30 ms after the jump through the verified endpoint. Mark the first newly detected period at or above 150 mm/s lasting at least 20 ms. An already elevated signal at the first eligible sample receives its own status. Separate missing endpoints and too-short intervals. The rule is a descriptive check on toward-target movement.

**Outward follow-through.** Start at the jump for D or movement onset for ND. Follow the cursor while the same final target center is logged, through the nominal deadline of 1 s after initial target appearance, the last logged sample or the last sample before a gap over 20 ms. Stop earlier if cursor motion turns back toward the starting area. The return proxy requires a trailing 30 ms backward screen-y speed of at least 50 mm/s for 30 ms with a net backward displacement of at least 20 px. Place the estimated outward end at the most forward sample in the 30 ms preceding the start of that return. Record the limiting reason, the outward-end distance and the minimum distance to the logged center over this segment. Keep the original verified manuscript endpoint and indicate whether it lies in the outward segment. These bounds use the mouse log and protocol timing.

**Fixed 250 ms steering.** Apply the same toward-target speed rule using the outward segment. An early detection must be confirmed by 250 ms after the jump, including the 20 ms sustain period. Later means confirmation after 250 ms, even when the qualifying period starts just before the cutoff. No detection means no qualifying period through the observed outward segment. If the outward segment ends before 250 ms, report incomplete separately. Keep the initially elevated status separate as well. Export the onset of detected steering through the outward segment for event alignment.

The report shows all matching trial counts, manuscript endpoint distances and closest observed distances. The path shows the manuscript endpoint, estimated outward end, closest approach and detected steering onset. Examples near the 10th, 50th and 90th endpoint-distance percentiles are shown by participant, session, displacement, manuscript label, 250 ms steering status and EEG eligibility. Each group can also display one example without a verified endpoint. The plots preserve the exact movement, jump, steering and endpoint samples among the displayed points.

**Observed target hit.** Run [audit_target_boundary.py](AUD_02_mouse_trajectories/audit_target_boundary.py) after the trajectory audit. It exports one label per accepted trial. A single sample at or inside the provisional 40 px circle around the logged final target center counts as a hit. Search from the jump (D) or movement onset (ND) through the last eligible sample, including any samples after the estimated outward endpoint. The label is hit detected or no hit detected. The observation cutoff is recorded separately.

**Boundary diagnostics.** The same script retains the 30, 40 and 50 px sensitivity checks. An endpoint can be classified only when the return proxy supplies one. For observed entry, a recorded sample at or inside the boundary counts from the jump (D) or movement onset (ND) through the estimated outward end. The two-sample check requires consecutive inside samples with different timestamps. Without observed entry, a return, nominal deadline or target change closes the search. A log cutoff or gap leaves entry indeterminate. The audit also flags first entries after the estimated outward end while the same target is still logged, through the existing target, deadline and gap limits.

~~~text
python Code/analyses/AUD_data_audit/AUD_02_mouse_trajectories/audit_target_boundary.py
~~~

See the [boundary audit results](../../../output/AUD_data_audit/AUD_02_mouse_trajectories/target_boundary/RESULTS.md) for the binary hit counts and links to the radius sensitivity checks.

| Saved output | Contents |
|---|---|
| [Results note](../../../output/AUD_data_audit/AUD_02_mouse_trajectories/RESULTS.md) | Cohort linkage, endpoint verification and implications for ERP grouping. |
| [Participant mapping](../../../output/AUD_data_audit/AUD_02_mouse_trajectories/participant_mapping.csv) | Inferred ID correspondence and displacement-sequence agreement. |
| [Trial audit](../../../output/AUD_data_audit/AUD_02_mouse_trajectories/trial_audit.csv.gz) | Manuscript label and verified endpoint, outward end and closest approach, both steering classifications and EEG eligibility. |
| [Coverage by session](../../../output/AUD_data_audit/AUD_02_mouse_trajectories/coverage_by_session.csv) | Counts by participant, session and displacement. |
