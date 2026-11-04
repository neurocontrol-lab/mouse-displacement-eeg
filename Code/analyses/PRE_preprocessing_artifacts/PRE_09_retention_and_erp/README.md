# PRE_09: Retention and matched ERP comparison

Map input flags to final decisions, screen accepted outputs and compare identical Correct/Error trial waveforms.

**Scope:** Two pilots; 2,562 trials in the four-condition intersection.
**Status:** Completed.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp)

## Inputs and dependencies

PRE_07 and PRE_08.

- [PRE_07 workflow](../PRE_07_boundary_analysis/README.md)

- [PRE_08 workflow](../PRE_08_input_quality/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [map_saved_decisions.m](map_saved_decisions.m) — Link input flags to each saved processing decision.
2. [summarise_retention.py](summarise_retention.py) — Summarise acceptance and rejection by flag.
3. [measure_final_quality.m](measure_final_quality.m) — Measure potential residual contamination after processing.
4. [analyse_final_quality.py](analyse_final_quality.py) — Summarise the output screens and select review examples.
5. [plot_retained_examples.m](plot_retained_examples.m) — Plot concerning retained examples.
6. [plot_residual_examples.m](plot_residual_examples.m) — Plot matched input/output residual examples.
7. [compare_matched_erp.m](compare_matched_erp.m) — Compute eight-channel means and response differences on the common trial intersection.
8. [summarise_matched_erp.py](summarise_matched_erp.py) — Summarise matched ERP changes.
9. [prepare_note_figures.m](prepare_note_figures.m) — Prepare the research-note figures from saved comparisons.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp')
map_saved_decisions.m
measure_final_quality.m
plot_retained_examples.m
plot_residual_examples.m
compare_matched_erp.m
prepare_note_figures.m
```

Python entry scripts (follow the numbered order above):

```text
.venv/Scripts/python.exe Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/summarise_retention.py
.venv/Scripts/python.exe Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/analyse_final_quality.py
.venv/Scripts/python.exe Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/summarise_matched_erp.py
```

## Settings and numerical interpretation

Four conditions retain their existing IDs: 1 = BP no-FORCe, 2 = BP FORCe, 3 = split no-FORCe, 4 = split FORCe. All use identical three-second input segments, the same one-second FORCe windows where applicable, a [-1,+1) s crop and [-0.2,0) s baseline. Cleaning boundaries are −0.5 and +0.5 s.

Comparisons using the four-condition intersection retain 2,562 matched trials. Check each table’s scope: quality-screen and own-acceptance summaries need not use this intersection. Suspected contamination, smoother traces and classification do not independently establish neural-signal preservation or ErrP identity.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/PRE_preprocessing_artifacts/report/index.html) · [Report files](../../../../output/PRE_preprocessing_artifacts/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
