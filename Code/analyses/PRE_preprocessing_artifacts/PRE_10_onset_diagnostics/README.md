# PRE_10: Individual-trial onset diagnostics

Inspect the earlier one-second/two-second onset discontinuities and revised preprocessing evidence.

**Scope:** Two pilots.
**Status:** Historical saved-output investigation.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics)

## Inputs and dependencies

Earlier pipeline outputs.

- [PRE_02 workflow](../PRE_02_force_1s_windows/README.md)

- [PRE_03 workflow](../PRE_03_force_2s_windows/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

This experiment preserves saved diagnostic outputs. No dedicated reproducible analysis entry script was present in the source repository; it is not presented as a fully rerunnable analysis.

## Settings and numerical interpretation

Read saved settings and the methods in the associated report. The saved configuration inside historical MAT files is provenance; it may retain the original filesystem paths. Scripts resolve current paths when loading those files.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/PRE_preprocessing_artifacts/report/index.html) · [Report files](../../../../output/PRE_preprocessing_artifacts/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
