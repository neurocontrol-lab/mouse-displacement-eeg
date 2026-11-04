# PRE_07: Boundary analysis

Compare four matched filtering/cleaning conditions, boundary changes and signal spreading.

**Scope:** Two pilots; 29 runs.
**Status:** Completed.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/PRE_preprocessing_artifacts/PRE_07_boundary_analysis)

## Inputs and dependencies

PRE_01 parsed metadata and raw recordings.

- [PRE_01 workflow](../PRE_01_no_force_reference/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [run_boundary_note.m](run_boundary_note.m) — Build/cache the four processing conditions; reruns FORCe only when needed.
2. [analyse_boundary_note.m](analyse_boundary_note.m) — Measure boundary changes, matched residuals, retention and figure diagnostics.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/PRE_preprocessing_artifacts/PRE_07_boundary_analysis')
run_boundary_note.m
analyse_boundary_note.m
```

## Settings and numerical interpretation

Four conditions retain their existing IDs: 1 = BP no-FORCe, 2 = BP FORCe, 3 = split no-FORCe, 4 = split FORCe. All use identical three-second input segments, the same one-second FORCe windows where applicable, a [-1,+1) s crop and [-0.2,0) s baseline. Cleaning boundaries are −0.5 and +0.5 s.

Comparisons using the four-condition intersection retain 2,562 matched trials. Check each table’s scope: quality-screen and own-acceptance summaries need not use this intersection. Suspected contamination, smoother traces and classification do not independently establish neural-signal preservation or ErrP identity.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/PRE_preprocessing_artifacts/PRE_07_boundary_analysis). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/PRE_preprocessing_artifacts/report/index.html) · [Report files](../../../../output/PRE_preprocessing_artifacts/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
