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

Within each recording, form as many D/ND pairs as possible without replacement while minimising the total absolute difference in time from initial target (300) to movement (400). Align each D trial to its recorded target displacement (500) and its ND control to the same delay after the control's movement. Retain the original continuous 1–20 Hz filtering, −200 to 0 ms movement baseline and DEC_02 acceptance decisions. Movement-aligned plots cover [−500, 900) ms and jump-aligned plots cover [−500, 500) ms. Marker times describe logged events. Screen onset was not measured independently.

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
