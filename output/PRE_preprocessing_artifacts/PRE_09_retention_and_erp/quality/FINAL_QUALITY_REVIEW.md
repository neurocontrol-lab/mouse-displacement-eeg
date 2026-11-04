# Final retained-signal quality assessment

## Main finding

Both possibilities raised in the discussion occur: filtering substantially attenuates some input features, while selected accepted outputs still contain concerning broad or local changes. Output screening also identifies candidates that were not flagged at input. None of these screens alone establishes an artifact source or certifies clean EEG.

The review uses the existing 29-recording, two-participant pilot; no FORCe optimisation, new rejection policy or production-pipeline change was made. All 180 >1 mV inputs remain rejected in all conditions.

## Measurements and reference

- All measurements use the same baseline-corrected retained [-1,+1) s signals and eight channels. HP-only context is measured on precisely the same samples, after the same baseline subtraction.
- One-sided Hann PSD estimates use 1,000 samples and 0.5 Hz spacing. Slow RMS covers 1–4 Hz; HF RMS covers 30–90 Hz excluding 48–52 Hz.
- Output slow RMS, full voltage range and maximum adjacent-sample change receive upper-tail modified z-scores on log features, with threshold 3.5. The fixed reference is accepted bandpass no-FORCe outputs from the same participant, session and channel. It is not re-estimated for cleaned outputs.
- The local-abrupt output screen additionally requires channel range at least three times the eight-channel median range. The combined output-review flag is the union of slow, range and local-abrupt flags.
- A separate boundary inspection flag requires a join step >3 times that channel/trial's ordinary-step 95th percentile. Ordinary steps exclude 50 ms around -0.5, 0 and +0.5 s. This arbitrary inspection ratio is reported separately, not as a confirmed contamination count.
- Upper-tail screens are descriptive. Range and slow-band outliers can include genuine neural responses; no significance test or diagnostic accuracy is claimed. Reference samples themselves may contain contamination and can mask persistent problems.
- Final metrics include any introduced joins because these are part of the signals actually retained for analysis. This does not change the one-second FORCe processing duration.
- Comparisons of HP input to final output measure the entire filtering/cleaning effect. Only FORCe versus its filtering-matched control can distinguish the added effect of FORCe. The original input screens used different one-second groups, so a changed flag is not automatically evidence of feature removal.

## Accepted input-flagged trials versus output review

Table entries are accepted input-flagged trials that meet any output-review criterion, divided by all accepted input-flagged trials. Boundary-only flags are separate.

| Participant | BP no-FORCe | BP FORCe | Split no-FORCe | Split FORCe |
|---|---:|---:|---:|---:|
| mle01 | 21 / 38 | 22 / 58 | 22 / 41 | 6 / 60 |
| spe30 | 8 / 96 | 4 / 97 | 8 / 96 | 0 / 97 |

These are review candidates, not numbers of confirmed unclean outputs. Passing the output screen does not prove an originally flagged artifact was removed.

## All accepted outputs

This includes outputs from input-unflagged trials. Different conditions have different accepted sets; the paired feature table below uses matched acceptance.

| Participant | Condition | Accepted | Slow | Range | Local | Any output flag | Input-unflagged with output flag | Boundary inspection |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| mle01 | BP no-FORCe | 1179 | 27 | 43 | 4 | 50 | 29 | 0 |
| mle01 | BP FORCe | 1201 | 15 | 18 | 40 | 63 | 41 | 797 |
| mle01 | Split no-FORCe | 1182 | 26 | 43 | 4 | 50 | 28 | 0 |
| mle01 | Split FORCe | 1203 | 10 | 2 | 0 | 12 | 6 | 6 |
| spe30 | BP no-FORCe | 1386 | 4 | 44 | 0 | 47 | 39 | 0 |
| spe30 | BP FORCe | 1387 | 0 | 14 | 0 | 14 | 10 | 1020 |
| spe30 | Split no-FORCe | 1386 | 4 | 43 | 0 | 46 | 38 | 0 |
| spe30 | Split FORCe | 1387 | 0 | 0 | 0 | 0 | 0 | 7 |

Flag categories overlap. Lower scores following FORCe could reflect useful attenuation or loss of relevant activity. In particular, zero output flags in spe30 split FORCe does not mean artifact-free or ERP-preserving output.

## Feature attenuation and persistence

- Among the 31 retained spe30 HF-flagged inputs, median matched-channel HF RMS is about 0.67% of HP input after bandpass no-FORCe, and 0.85% after split no-FORCe (about 99.3% and 99.1% attenuation). This is expected from the low-pass and must not be credited to FORCe. These are RMS ratios, not percentages of artifacts removed.
- Among four retained mle01 local-input flags, the median maximum-step ratio after either no-FORCe filtering scheme is about 4% of matched HP input. Yet a broad P3 deflection remains in one reviewed trial. Attenuating a sharp change does not guarantee disappearance of a broader disturbance.
- Bandpass FORCe can introduce sharp joins after its last filter. The separate boundary screen is positive in 797/1,201 mle01 and 1,020/1,387 spe30 accepted outputs, versus zero in either no-FORCe control. Split FORCe has six and seven such cases. This is an inspection ratio, not an artifact prevalence estimate.
- Bandpass FORCe creates 33 new combined output-screen candidates in mle01 and one in spe30 among trials accepted by both it and its matched control. This concerns changed signal features, not independent proof of neural damage.

## Visual review

Fourteen inputs and their final eight-channel outputs were inspected: focused residual candidates, cases newly flagged after processing, and one randomly selected input-unflagged accepted trial per participant/session (six total). Random selection uses seed 20261021; the small visual sample does not estimate prevalence. Expert fields remain blank in `residual_visual_review.csv`.

| Review | Trial | Initial assessment | Plot |
|---|---|---|---|
| 1 | mle01 / retest / run 1 / trial 10 | feature remains concerning in controls; attenuated with FORCe | [Open](residual_figures/accepted_review_01.png) |
| 2 | mle01 / post / run 4 / trial 40 | feature remains concerning in controls | [Open](residual_figures/accepted_review_02.png) |
| 3 | mle01 / post / run 3 / trial 82 | input screen overlooked a concerning retained feature | [Open](residual_figures/accepted_review_03.png) |
| 4 | mle01 / pre / run 1 / trial 70 | new processing-related change | [Open](residual_figures/accepted_review_04.png) |
| 5 | mle01 / pre / run 4 / trial 11 | uncertain; no output screen flag in reference condition | [Open](residual_figures/accepted_review_05.png) |
| 6 | mle01 / post / run 3 / trial 17 | uncertain; output range review flag | [Open](residual_figures/accepted_review_06.png) |
| 7 | mle01 / retest / run 5 / trial 35 | uncertain; no output screen flag in reference condition | [Open](residual_figures/accepted_review_07.png) |
| 8 | spe30 / post / run 4 / trial 5 | uncertain; no output screen flag in reference condition | [Open](residual_figures/accepted_review_08.png) |
| 9 | spe30 / retest / run 5 / trial 1 | higher-frequency feature attenuated; separate residual concern | [Open](residual_figures/accepted_review_09.png) |
| 10 | spe30 / retest / run 5 / trial 80 | input screen overlooked a concerning retained feature | [Open](residual_figures/accepted_review_10.png) |
| 11 | spe30 / post / run 5 / trial 68 | new output-screen flag after processing; source uncertain | [Open](residual_figures/accepted_review_11.png) |
| 12 | spe30 / pre / run 5 / trial 55 | uncertain; no output screen flag in reference condition | [Open](residual_figures/accepted_review_12.png) |
| 13 | spe30 / post / run 1 / trial 6 | uncertain; no output screen flag in reference condition | [Open](residual_figures/accepted_review_13.png) |
| 14 | spe30 / retest / run 4 / trial 32 | uncertain; no output screen flag in reference condition | [Open](residual_figures/accepted_review_14.png) |

### Priority cases

- **Review 2, mle01 post run 4 trial 40:** P3-local broad deflection remains in both accepted no-FORCe controls. Both FORCe prechecks reject it.
- **Review 3, mle01 post run 3 trial 82:** input-unflagged trial with substantial P3-local excursions still present in both controls, below the 100 µV acceptance threshold.
- **Review 10, spe30 retest run 5 trial 80:** input-unflagged CP5-local change around +0.4 s leaves a broad transition in the no-FORCe outputs. It overlaps the response interval and warrants expert review.
- **Review 4, mle01 pre run 1 trial 70:** bandpass FORCe has a CP1 step of 6.079 µV exactly at +0.5 s. This directly links a newly flagged change to a cleaning join.

## Conclusion for this step

The primary no-FORCe pipeline handles the gross pilot disturbances and suppresses the measured HF feature substantially. It does not automatically exclude every concerning smaller/local waveform. A focused expert review of the priority cases is warranted before accepting the rejection policy as sufficient or adding new exclusions. The next ERP comparison should retain matched trial IDs; lower residual scores alone cannot select the cleaning method.

## Reproduction and saved data

1. Run `measure_final_quality.m` in MATLAB.
2. Run `analyse_final_quality.py` with Python/numpy.
3. Run `plot_residual_examples.m` in MATLAB.

- `final_channel_metrics.csv`: identical-window input/output feature measurements.
- `final_screen_reference.csv`: fixed reference group sizes, log medians and MADs.
- `final_channel_screen.csv`, `final_trial_screen.csv`: scores and flags with original decisions.
- `final_quality_summary.csv`: participant/session/run summaries, separately by displaced/non-displaced class.
- `paired_final_features.csv`: same-trial/channel ratios with matching filtering controls.
- `residual_review_selection.csv`, `residual_visual_review.csv`, `residual_figures/`: review selection, initial observations and plots.

Initial visual observations are descriptive, not independent expert labels. The review does not change earlier reports or the production pipeline.
