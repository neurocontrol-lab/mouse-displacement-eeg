# FEA_01: Feature audit and repeatability

Compare channel sets, time-point amplitudes, 100 ms bins and within-participant waveform repeatability.

**Scope:** Two pilots; 2,562 matched trials.
**Status:** Completed.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/FEA_features_repeatability/FEA_01_feature_audit)

## Inputs and dependencies

PRE_07 and PRE_09.

- [PRE_07 workflow](../../PRE_preprocessing_artifacts/PRE_07_boundary_analysis/README.md)

- [PRE_09 workflow](../../PRE_preprocessing_artifacts/PRE_09_retention_and_erp/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [extract_matched_features.m](extract_matched_features.m) — Export matched sample-wise and 100 ms feature data.
2. [analyse_feature_audit.py](analyse_feature_audit.py) — Summarise feature separation and binning effects.
3. [plot_feature_audit.m](plot_feature_audit.m) — Draw channel/time feature comparisons.
4. [check_repeatability.m](check_repeatability.m) — Calculate the existing split-half, between-run and between-session checks.
5. [summarise_repeatability.py](summarise_repeatability.py) — Summarise repeatability.
6. [plot_repeatability.m](plot_repeatability.m) — Generate the repeatability figures.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/FEA_features_repeatability/FEA_01_feature_audit')
extract_matched_features.m
plot_feature_audit.m
check_repeatability.m
plot_repeatability.m
```

Python entry scripts (follow the numbered order above):

```text
.venv/Scripts/python.exe Code/analyses/FEA_features_repeatability/FEA_01_feature_audit/analyse_feature_audit.py
.venv/Scripts/python.exe Code/analyses/FEA_features_repeatability/FEA_01_feature_audit/summarise_repeatability.py
```

## Settings and numerical interpretation

Four conditions retain their existing IDs: 1 = BP no-FORCe, 2 = BP FORCe, 3 = split no-FORCe, 4 = split FORCe. All use identical three-second input segments, the same one-second FORCe windows where applicable, a [-1,+1) s crop and [-0.2,0) s baseline. Cleaning boundaries are −0.5 and +0.5 s.

Comparisons using the four-condition intersection retain 2,562 matched trials. Check each table’s scope: quality-screen and own-acceptance summaries need not use this intersection. Suspected contamination, smoother traces and classification do not independently establish neural-signal preservation or ErrP identity.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/FEA_features_repeatability/FEA_01_feature_audit). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/FEA_features_repeatability/report/index.html) · [Report files](../../../../output/FEA_features_repeatability/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
