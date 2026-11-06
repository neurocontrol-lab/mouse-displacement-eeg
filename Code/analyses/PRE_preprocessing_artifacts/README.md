# PRE — Preprocessing and artifact handling

How do filtering, FORCe windows and quality/rejection rules affect movement-aligned EEG? The experiments include shared preprocessing, input screening, reconstruction-boundary checks and matched signal comparisons.

[Experiment registry](../../../EXPERIMENTS.md) · [Interactive report](../../../output/PRE_preprocessing_artifacts/report/index.html)

## Experiments

| ID | Analysis | Scope | Results |
|---|---|---|---|
| [PRE_01](#pre_01) | No-FORCe reference | 25 available participants | [Open](../../../output/PRE_preprocessing_artifacts/PRE_01_no_force_reference/) |
| [PRE_02](#pre_02) | One-second FORCe windows | mle01 and spe30; 29 runs | [Open](../../../output/PRE_preprocessing_artifacts/PRE_02_force_1s_windows/) |
| [PRE_03](#pre_03) | Two-second FORCe windows | Two pilots; 29 runs | [Open](../../../output/PRE_preprocessing_artifacts/PRE_03_force_2s_windows/) |
| [PRE_04](#pre_04) | Split filtering | Two pilots; 29 runs | [Open](../../../output/PRE_preprocessing_artifacts/PRE_04_split_filtering/) |
| [PRE_05](#pre_05) | FORCe coding fixes | Two pilots; 29 runs | [Open](../../../output/PRE_preprocessing_artifacts/PRE_05_force_coding_fixes/) |
| [PRE_06](#pre_06) | Full-cohort FORCe run | 25 available participants | [Open](../../../output/PRE_preprocessing_artifacts/PRE_06_force_full_cohort/) |
| [PRE_07](#pre_07) | Boundary analysis | Two pilots; 29 runs | [Open](../../../output/PRE_preprocessing_artifacts/PRE_07_boundary_analysis/) |
| [PRE_08](#pre_08) | Input-quality screen | Two pilots; all eight channels | [Open](../../../output/PRE_preprocessing_artifacts/PRE_08_input_quality/) |
| [PRE_09](#pre_09) | Retention and matched ERP comparison | Two pilots; 2,562 trials in the four-condition intersection | [Open](../../../output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/) |
| [PRE_10](#pre_10) | Individual-trial onset diagnostics | Two pilots | [Open](../../../output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics/) |

## Shared conventions

EEG is sampled at 500 Hz across P3, PO3, PO7, CP5, CP1, Cz, FCz and FC1. Raw voltages are converted from nV to µV. Labels 1/2 mean non-displaced/Correct and displaced/Error. Error − Correct is displaced minus non-displaced; these names do not verify an error percept.

Run commands from the repository root. MATLAB analysis uses Signal Processing Toolbox and, where needed, Statistics and Machine Learning Toolbox. Executing FORCe also requires Wavelet Toolbox and the supplied Windows x64 binaries. Install Python dependencies using `python -m pip install -r requirements-analysis.txt`.

PRE_01–06 use the [shared preprocessing stages](../../preprocessing/README.md). Historical FORCe code changed after some results were saved; current settings alone do not guarantee identical historical reconstructions. PRE_01 is the saved no-FORCe reference.

PRE_07 and PRE_09 retain processing-condition IDs: 1 = BP no-FORCe; 2 = BP FORCe; 3 = split no-FORCe; 4 = split FORCe. These use the same three-second input context, one-second cleaning windows where applicable, [-1,+1) s crop and [-0.2,0) s baseline. Joins are −0.5 and +0.5 s.

## Shared stage workflow

| Step | Script | Operation |
|---|---|---|
| 1 | [stage01_parse_events.m](../../preprocessing/stage01_parse_events.m) | Construct or reuse the shared event metadata. |
| 2 | [stage02_preprocess_epochs.m](../../preprocessing/stage02_preprocess_epochs.m) | Process the selected PRE configuration; saved PRE_01 reference outputs are protected. |
| 3 | [stage03_plot_errp.m](../../preprocessing/stage03_plot_errp.m) | Draw participant/session means and exploratory waveform statistics. |
| 4, optional | [stage04_group_averages.m](../../preprocessing/stage04_group_averages.m) | Form equal-participant session summaries. |

Select a PRE configuration explicitly. For example:

```matlab
addpath('Code', 'Code/preprocessing')
cfg = config('PRE_02');
stage01_parse_events
```

For signal processing or plotting, follow the [shared stage instructions](../../preprocessing/README.md). Historical reconstructions are reviewed through their saved outputs.

## PRE_01

**No-FORCe reference.** Shared event parsing and continuous 1–20 Hz filtering, followed by two-second epochs, baseline and rejection.

**Scope:** 25 available participants.

Use the shared stage workflow with `cfg = config('PRE_01')`.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_01_no_force_reference/).

## PRE_02

**One-second FORCe windows.** Compare two independently cleaned one-second halves joined at movement onset.

**Scope:** mle01 and spe30; 29 runs.

Use the shared stage workflow with `cfg = config('PRE_02')`.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_02_force_1s_windows/).

## PRE_03

**Two-second FORCe windows.** Test whether cleaning the full two-second epoch reduces the onset discontinuity.

**Scope:** Two pilots; 29 runs.

Use the shared stage workflow with `cfg = config('PRE_03')`.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_03_force_2s_windows/).

## PRE_04

**Split filtering.** Apply continuous 1 Hz high-pass before two-second FORCe and epoch 20 Hz low-pass afterward.

**Scope:** Two pilots; 29 runs.

Use the shared stage workflow with `cfg = config('PRE_04')`.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_04_split_filtering/).

## PRE_05

**FORCe coding fixes.** Compare the then-current coding corrections with the preceding split-filter output.

**Scope:** Two pilots; 29 runs.

Use the shared stage workflow with `cfg = config('PRE_05')`.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_05_force_coding_fixes/).

## PRE_06

**Full-cohort FORCe run.** Earlier all-participant FORCe visual review. This is separate from the primary no-FORCe decoder analysis.

**Scope:** 25 available participants.

Use the shared stage workflow with `cfg = config('PRE_06')`.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_06_force_full_cohort/).

## PRE_07

**Boundary analysis.** Compare four matched filtering/cleaning conditions, boundary changes and signal spreading.

**Scope:** Two pilots; 29 runs.

| Step | Script | Operation |
|---|---|---|
| 1 | [run_boundary_note.m](PRE_07_boundary_analysis/run_boundary_note.m) | Build/cache the four processing conditions; reruns FORCe only when needed. |
| 2 | [analyse_boundary_note.m](PRE_07_boundary_analysis/analyse_boundary_note.m) | Measure boundary changes, matched residuals, retention and figure diagnostics. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/PRE_preprocessing_artifacts/PRE_07_boundary_analysis')
run_boundary_note
analyse_boundary_note
```


[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_07_boundary_analysis/).

## PRE_08

**Input-quality screen.** Characterise suspected input contamination in one-second windows before reviewing cleaner outputs.

**Scope:** Two pilots; all eight channels.

| Step | Script | Operation |
|---|---|---|
| 1 | [run_input_screen.m](PRE_08_input_quality/run_input_screen.m) | Screen raw/continuous-high-pass inputs in one-second windows. |
| 2 | [summarise_inputs.py](PRE_08_input_quality/summarise_inputs.py) | Summarise flag prevalence and review selection. |
| 3 | [plot_input_review.m](PRE_08_input_quality/plot_input_review.m) | Draw the input-only review examples. |
| 4 | [finish_review.m](PRE_08_input_quality/finish_review.m) | Complete the saved review illustrations and target-aligned summaries. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/PRE_preprocessing_artifacts/PRE_08_input_quality')
run_input_screen
plot_input_review
finish_review
```

```text
python Code/analyses/PRE_preprocessing_artifacts/PRE_08_input_quality/summarise_inputs.py
```


[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_08_input_quality/).

## PRE_09

**Retention and matched ERP comparison.** Map input flags to final decisions, screen accepted outputs and compare identical Correct/Error trial waveforms.

**Scope:** Two pilots; 2,562 trials in the four-condition intersection.

| Step | Script | Operation |
|---|---|---|
| 1 | [map_saved_decisions.m](PRE_09_retention_and_erp/map_saved_decisions.m) | Link input flags to each saved processing decision. |
| 2 | [summarise_retention.py](PRE_09_retention_and_erp/summarise_retention.py) | Summarise acceptance and rejection by flag. |
| 3 | [measure_final_quality.m](PRE_09_retention_and_erp/measure_final_quality.m) | Measure potential residual contamination after processing. |
| 4 | [analyse_final_quality.py](PRE_09_retention_and_erp/analyse_final_quality.py) | Summarise the output screens and select review examples. |
| 5 | [plot_retained_examples.m](PRE_09_retention_and_erp/plot_retained_examples.m) | Plot concerning retained examples. |
| 6 | [plot_residual_examples.m](PRE_09_retention_and_erp/plot_residual_examples.m) | Plot matched input/output residual examples. |
| 7 | [compare_matched_erp.m](PRE_09_retention_and_erp/compare_matched_erp.m) | Compute eight-channel means and response differences on the common trial intersection. |
| 8 | [summarise_matched_erp.py](PRE_09_retention_and_erp/summarise_matched_erp.py) | Summarise matched ERP changes. |
| 9 | [prepare_note_figures.m](PRE_09_retention_and_erp/prepare_note_figures.m) | Prepare the research-note figures from saved comparisons. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp')
map_saved_decisions
measure_final_quality
plot_retained_examples
plot_residual_examples
compare_matched_erp
prepare_note_figures
```

```text
python Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/summarise_retention.py
python Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/analyse_final_quality.py
python Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/summarise_matched_erp.py
```


[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/).

## PRE_10

**Individual-trial onset diagnostics.** Inspect the earlier one-second/two-second onset discontinuities and revised preprocessing evidence.

**Scope:** Two pilots.

Saved-output evidence only. A dedicated reproducible entry script was not present in the supplied analysis materials. Review the [results](../../../output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics/) and associated note.

[Saved numerical results and figures](../../../output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics/).

## Interactive waveform view

The [PRE report](../../../output/PRE_preprocessing_artifacts/report/index.html) defaults to BP no-FORCe and all accepted trials for all 25 participants, separately by pre/post/retest. Each view shows Correct, Error and Error−Correct on all eight channels, counts, consistent axes across sessions within each participant/channel, and a PNG download. Sessions ineligible for classification remain visible and are labelled.

The primary averages use the accepted trial IDs in DEC_02, including its complete-three-second quality checks. The other three conditions are available only for mle01 and spe30 from PRE_07. **All accepted trials** uses each condition's own accepted IDs; **matched** uses the intersection accepted by all four pilot conditions. Matching does not equalise Correct and Error counts. The BP overlay follows the selected trial mode. Matching and the other conditions are disabled for participants without those outputs. The historical two-second FORCe cohort run is separate.

Waveform, saved-figure and numerical-table controls are independent. Pilot condition/trial-mode choices are remembered when moving through participants with only the primary condition. The three saved PRE images are fixed pilot figures and therefore have only a figure selector, with a description that updates for the selected image. The numerical-summary section is explicitly pilot-only (mle01 and spe30), including its pooled rows. Numerical tables expose their own available participant, session, condition, waveform, summary-level and other relevant filters; each table remembers its selections. Controls only offer fields present in the selected table.

| Step | Script | Operation |
|---|---|---|
| 1, when refreshing means | [export_report_waveforms.m](../../helpers/export_report_waveforms.m) | Aggregate saved PRE_01 epochs on DEC_02 IDs and saved PRE_07 pilot epochs; export `waveform_means.json` beside the report. No preprocessing or FORCe is rerun. |
| 2 | [build_web_reports.py](../../helpers/build_web_reports.py) | Embed the exported means and saved summaries into the portable HTML report. |

```matlab
run('Code/helpers/export_report_waveforms.m')
```

```text
python Code/helpers/build_web_reports.py --category PRE_preprocessing_artifacts
```

## Research note

The category report folder contains the interactive HTML overview, formal PDF and editable LaTeX. The reviewed LaTeX is the authoritative manuscript source. To rebuild the HTML overviews from saved results: `python Code/helpers/build_web_reports.py`.
