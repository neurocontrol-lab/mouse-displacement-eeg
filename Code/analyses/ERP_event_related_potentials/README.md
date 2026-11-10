# ERP — Event-related potentials

Compare event-aligned EEG waveforms, their timing and their morphology across conditions and participants.

[Experiment registry](../../../EXPERIMENTS.md) · [Interactive report](../../../output/ERP_event_related_potentials/report/index.html)

## ERP_01

**Movement and target-jump alignment.** Compare displaced (D), non-displaced (ND) and D − ND waveforms using identical trials for both alignments.

| Step | Script | Operation |
|---|---|---|
| 1 | [extract_matched_waveforms.m](ERP_01_event_locked_waveforms/extract_matched_waveforms.m) | Match DEC_02 accepted trials, re-index the saved PRE_01 no-FORCe epochs and extract run-level window means. |
| 2 | [analyse_waveforms.py](ERP_01_event_locked_waveforms/analyse_waveforms.py) | Generate waveforms, coverage, fixed-window cohort tests and individual estimates with intervals. |
| 3 | [build_web_reports.py](../../helpers/build_web_reports.py) | Assemble the interactive report from the saved aggregates. |

Run from the repository root.

~~~matlab
addpath('Code/analyses/ERP_event_related_potentials/ERP_01_event_locked_waveforms')
extract_matched_waveforms
~~~

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_01_event_locked_waveforms/analyse_waveforms.py
python Code/helpers/build_web_reports.py --category ERP_event_related_potentials
~~~

Within each recording, form as many D/ND pairs as possible without replacement while minimising the total absolute difference in time from initial target (300) to movement (400). Align each D trial to its recorded target displacement (500) and its ND control to the same delay after the control's movement. Retain the original continuous 1–20 Hz filtering, −200 to 0 ms movement baseline and DEC_02 acceptance decisions. Movement-aligned plots cover [−500, 900) ms and jump-aligned plots cover [−500, 500) ms. Marker times describe logged events. Screen onset was not measured independently. [AUD_01](../AUD_data_audit/README.md#aud_01) audits the movement and jump markers. [AUD_02](../AUD_data_audit/README.md#aud_02) audits reach trajectories and behavioural labels.

| Morphology check | Alignment | Electrodes | Window (ms) | Expected sign of D − ND |
|---|---|---|---|---|
| ERN-like | Movement and jump, separately | Cz, FCz | [50, 100) | Negative |
| Pe-like | Movement and jump, separately | CP1 | [200, 500) | Positive |
| Interaction negativity | Jump | Cz, FCz | [200, 280) | Negative |
| Interaction positivity | Jump | Cz, FCz | [280, 360) | Positive |
| Graz negativity | Movement | Cz, FCz | [400, 600) | Negative |
| Graz positivity | Movement | Cz, FCz | [650, 750) | Positive |

The windows were set before examining these waveforms. The first two use conventional response-locked timings as a morphology check, with CP1 as the available centroparietal site and a broad 200–500 ms positivity window. The interaction windows bracket the negative and positive deflections near 250 and 320 ms. The Graz windows cover the later movement-locked deflections described for the two original participants. [Response-locked ERN/Pe study](https://pmc.ncbi.nlm.nih.gov/articles/PMC3314233/) · [Interaction ErrP study](https://pubmed.ncbi.nlm.nih.gov/18334383/) · [Graz paper](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf)

Average the samples and listed electrodes in each window. Pool matched pairs across sessions within each participant, then give each participant equal weight. Test the participant D − ND means using two-sided one-sample t-tests. Report marginal 95% confidence intervals and Holm adjustment across the eight planned comparisons on the 23 non-pilot participants. Report both pilots and individual sessions descriptively. For the timing check, split the pairs in each recording into equally sized short and long delay groups, breaking ties by D trial ID and omitting the middle pair for odd counts. Plot the group differences under each alignment.

**Individual repeatability.** Use the same eight windows and matched pairs for all 25 participants. Show each participant's pair-weighted pooled D − ND amplitude, session means, and run means. For a pooled 95% percentile interval, draw 20,000 bootstrap samples by resampling whole runs with replacement within each session. Within each draw, weight the selected runs by their matched-pair counts, then combine the session means with the original session pair weights. Each interval is marginal and describes run-to-run uncertainty conditional on the observed sessions. A session with one run contributes a fixed estimate to the pooled interval. Use session and run estimates descriptively to compare sign and size.

The [output folder](../../../output/ERP_event_related_potentials/ERP_01_event_locked_waveforms/) contains matched trial IDs, participant/session match coverage, component estimates at the participant, session and run levels, and figures. The contrast includes possible visual and corrective-movement responses alongside error-related activity. A component-window test assesses the mean voltage in that window.

**Results.** Matching retained 10,153 D/ND pairs, including 9,269 from non-pilot participants. The median absolute reaction-time difference within pairs was 2 ms (95th percentile 28 ms). The classic ERN/Pe checks and the later Graz windows did not reach the Holm-adjusted threshold in non-pilots. The sole adjusted result was positive D − ND at Cz/FCz from 200 to 280 ms after the jump (+2.06 µV, 95% CI 1.00 to 3.13 µV, Holm p = .0044), opposite the interaction template's predicted sign. A positive deflection near 270 ms was visible in the cohort plots across sessions and both delay groups. In the 200–280 ms window, 9 of 23 non-pilot participants had a positive session mean at pre, post and retest. The other 14 had mixed signs. The two pilots showed the expected signs in both later Graz windows, with larger mean differences than the non-pilot group.

The interactive report shows all eight channels and lets you select an alignment, participant or cohort, session and delay group. The repeatability view compares pooled estimates and intervals across participants and shows run and session means for the selected participant. The report also includes saved figures, group tests and match coverage. Waveform samples are displayed at 2 ms intervals with stored values rounded to 0.01 µV. The saved numerical tests use the full precision of the input. Rebuild only the HTML by running step 3 with the saved ERP_01 results.

## ERP_02

**Steering and endpoint distance.** Keep ERP_01 as the displaced (D) versus matched non-displaced (ND) reference. Within D, ask whether the jump-aligned response differs with detected steering and how it varies with distance to the final target. Plot a separate alignment to detected steering onset.

| Step | Script | Operation |
|---|---|---|
| 1 | [prepare_steering_trials.py](ERP_02_steering_and_endpoint/prepare_steering_trials.py) | Link the accepted D trials to the AUD_01 markers and AUD_02 behavioural measures. Select matching pairs and define the EEG windows. |
| 2 | [extract_steering_waveforms.m](ERP_02_steering_and_endpoint/extract_steering_waveforms.m) | Re-index the saved PRE_01 EEG and compute waveforms and window means. |
| 3 | [analyse_steering_waveforms.py](ERP_02_steering_and_endpoint/analyse_steering_waveforms.py) | Plot the waveform contrasts and alignments, and summarise distance slopes and coverage. |
| 4 | [build_web_reports.py](../../helpers/build_web_reports.py) | Add the results to the ERP interactive report. |

Run from the repository root with PRE_01 processed EEG, DEC_02 trial IDs and the AUD_01/AUD_02 trial tables available. Run these commands in order.

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_02_steering_and_endpoint/prepare_steering_trials.py
~~~

~~~matlab
addpath('Code/analyses/ERP_event_related_potentials/ERP_02_steering_and_endpoint')
extract_steering_waveforms
~~~

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_02_steering_and_endpoint/analyse_steering_waveforms.py
python Code/helpers/build_web_reports.py --category ERP_event_related_potentials
~~~

**Jump alignment.** Compare D with steering confirmed by 250 ms to D with no confirmation by 250 ms. Require complete outward observation through 250 ms and exclude trials already over the threshold when the search starts. Match as many pairs as possible within recording and jump side, without replacement, minimising the summed absolute gaps in reaction time and movement-to-jump delay. Show the combined contrast and separately show the pairs whose control steered later or had no detection in the observed outward reach. Plot [−500, +500) ms relative to EEG marker 500. Summarise the four ERP_01 jump windows and a descriptive posterior window at P3, PO3 and PO7 from 200 to 400 ms. Pool session means by pair count within each participant and weight non-pilot participants equally.

**Steering alignment.** For trials with an onset detected anywhere in the observed outward reach, add the mouse jump-to-steering interval to EEG marker 500 and round the interval to the nearest EEG sample. Show [−1,000, +500) ms around steering if supported by the saved movement epoch. Show the same trials around the jump for comparison. Both views retain the −200 to 0 ms movement baseline and the continuous 1–20 Hz no-FORCe signal. Weight the available trials equally within participant, then weight the non-pilot participants equally.

**Distance.** Use the minimum distance over the full eligible mouse log as the primary measure. Compare it with outward-only minimum distance and manuscript endpoint distance on the same trials, each with a verified manuscript endpoint in the outward segment. The full-log minimum comes from the AUD_02 observed-hit export. Estimate each slope within participant after centring by recording and jump side and adjusting for reaction time and jump delay. Report µV per 100 px farther from the target center. All ERP_02 comparisons are descriptive. A detected steering onset is a behavioural threshold crossing, and target geometry and a timed outcome cue remain unverified.

[Results note](../../../output/ERP_event_related_potentials/ERP_02_steering_and_endpoint/RESULTS.md) · [Interactive report](../../../output/ERP_event_related_potentials/report/index.html)

## ERP_03

**Corrective versus erroneous displaced reaches.** Compare the jump-aligned EEG for the two supplied manuscript trajectory classes. The classes combine lateral velocity and endpoint distributions. Keep the AUD_02 steering proxy and geometric target outcome as separate measures.

| Step | Script | Operation |
|---|---|---|
| 1 | [compare_trajectories.py](ERP_03_corrective_trajectories/compare_trajectories.py) | Join manuscript labels to the accepted ERP_02 displaced trial IDs and match pairs. |
| 2 | [extract_trajectory_waveforms.m](ERP_03_corrective_trajectories/extract_trajectory_waveforms.m) | Re-index the saved PRE_01 epochs to EEG marker 500 and sum the matched traces by participant and session. |
| 3 | [compare_trajectories.py](ERP_03_corrective_trajectories/compare_trajectories.py) | Export the eight-channel figure, browser waveform means, coverage and window amplitudes. |
| 4 | [build_web_reports.py](../../helpers/build_web_reports.py) | Build the ERP report with the new waveform and tables. |

Run from the repository root with the AUD_02 and ERP_02 trial tables and saved PRE_01 EEG available.

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_03_corrective_trajectories/compare_trajectories.py prepare
~~~

~~~matlab
addpath('Code/analyses/ERP_event_related_potentials/ERP_03_corrective_trajectories')
extract_trajectory_waveforms
~~~

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_03_corrective_trajectories/compare_trajectories.py summarise
python Code/helpers/build_web_reports.py --category ERP_event_related_potentials
~~~

Use the accepted displaced trials labelled corrective or erroneous. Exclude the other manuscript labels. Within each recording and jump direction, form as many pairs as possible without replacement while minimising the summed absolute gaps in reaction time and movement-to-jump delay. Retain PRE_01 continuous 1–20 Hz no-FORCe filtering and the original [−200, 0) ms movement baseline. Plot [−500, +500) ms after the logged jump and use the five ERP_02 jump-aligned amplitude windows. Pool pairs across sessions within each participant, then weight contributing participants equally for the cohort summaries. Report pilots separately. The comparison is descriptive.

[Results note](../../../output/ERP_event_related_potentials/ERP_03_corrective_trajectories/RESULTS.md) · [Interactive report](../../../output/ERP_event_related_potentials/report/index.html)

## ERP_04

**Observed target entry and close approach.** Compare jump-aligned waveforms using the provisional geometric labels from AUD_02. Use five contrasts.

| Contrast | Reference | Comparison |
|---|---|---|
| Observed hit | D no hit detected | D entered the 40 px circle anywhere in the eligible log |
| Common observation | D no hit by 400 ms | D hit by 400 ms |
| Close approach | D no approach within 75 px | D reached within 75 px |
| Radius sensitivity | D no approach within 100 px | D reached within 100 px |
| Matched hits | ND hit after its paired pseudo-jump | D hit after the target jump |

The 400 ms contrast requires both groups to have logged samples through 400 ms after the jump. Later hits count in the no-hit-by-400 ms group for that contrast. For the within-D contrasts, maximise pairs without replacement within recording and jump side, then minimise summed absolute reaction-time and movement-to-jump delay gaps. For matched D and ND hits, pair within recording on reaction time and give the ND trial the same movement-to-jump delay as its D pair. Require ND entry at or after that pseudo-jump.

| Step | Script | Operation |
|---|---|---|
| 1 | [compare_observed_outcomes.py](ERP_04_observed_target_entry/compare_observed_outcomes.py) | Join AUD_01 marker timing, AUD_02 outcome labels and DEC_02 trial IDs. Match pairs and export coverage. |
| 2 | [extract_outcome_waveforms.m](ERP_04_observed_target_entry/extract_outcome_waveforms.m) | Extract paired traces from the saved PRE_01 no-FORCe epochs. |
| 3 | [compare_observed_outcomes.py](ERP_04_observed_target_entry/compare_observed_outcomes.py) | Export eight-channel figures, browser waveforms and descriptive window amplitudes. |
| 4 | [analyse_matched_hit_timing.py](ERP_04_observed_target_entry/analyse_matched_hit_timing.py) | Test pooled central and posterior time clusters and the fixed posterior N100 window. |
| 5 | [build_web_reports.py](../../helpers/build_web_reports.py) | Build the interactive report. |

Run from the repository root with the AUD_01 and AUD_02 tables, DEC_02 trial IDs, ERP_02 windows and PRE_01 EEG available.

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_04_observed_target_entry/compare_observed_outcomes.py prepare
~~~

~~~matlab
addpath('Code/analyses/ERP_event_related_potentials/ERP_04_observed_target_entry')
extract_outcome_waveforms
~~~

~~~text
python Code/analyses/ERP_event_related_potentials/ERP_04_observed_target_entry/compare_observed_outcomes.py summarise
python Code/analyses/ERP_event_related_potentials/ERP_04_observed_target_entry/analyse_matched_hit_timing.py
python Code/helpers/build_web_reports.py --category ERP_event_related_potentials
~~~

Use the original PRE_01 1–20 Hz signal and [−200, 0) ms movement baseline. Plot [−500, +500) ms about the jump or pseudo-jump and reuse the five ERP_02 amplitude windows. Pool pairs across sessions within each participant, then weight contributing participants equally. Keep the pilots separate. The comparison describes observed entry and proximity. The radius and task scoring remain provisional, and shorter logs limit the interpretation of no observed hit. For the matched D-hit versus ND-hit contrast, the exploratory follow-up uses two-sided tests of one pooled difference per non-pilot participant. Report marginal 95% confidence intervals and Holm adjustment across the five ERP_04 windows. This family is separate from the eight ERP_01 tests.

[Results note](../../../output/ERP_event_related_potentials/ERP_04_observed_target_entry/RESULTS.md) · [Interactive report](../../../output/ERP_event_related_potentials/report/index.html#savedFigures)

The interactive report has direct sections for cohort window tests and distance associations. The distance section can show all eligible displaced trials or split them by observed entry into the provisional 40 px target circle. In **Explore the matched waveforms**, select ERP_04 to show D hits versus matched ND hits at the jump or pseudo-jump. The timing controls show the supported pooled non-pilot clusters and the separate exploratory posterior N100 window. In the waveform gallery, the ERP morphology selector shades the listed channels and time range on compatible event alignments. Candidate feedback windows are listed for reference until a verified outcome cue is available. The morphology overlays are independent of the statistical tests.

**Matched-hit timing follow-up.** Pool the 40 px D-hit minus ND-hit pairs within each non-pilot participant. Average Cz/FCz and P3/PO3/PO7 separately and search [0, 500) ms after the jump or pseudo-jump. Form same-sign temporal clusters within each region using the two-sided uncorrected .05 t threshold. Use the sum of absolute t values for each cluster. For each of 19,999 random sign flips (seed 2026), apply one sign per participant jointly to both regions and all times, then retain the maximum mass across both regions and polarities. The corrected p-value includes the observed assignment. The sign-flip null assumes symmetry of participant differences. Use the pooled cluster windows for descriptive pre, post and retest estimates. The interval edges depend on the search and cluster-forming threshold.

Test the posterior N100-like morphology at P3/PO3/PO7 from [80, 150) ms in a separate two-sided fixed-window check. Report the mean difference, marginal 95% interval and nominal p-value.
