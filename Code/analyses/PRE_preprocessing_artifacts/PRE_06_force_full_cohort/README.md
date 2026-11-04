# PRE_06: Full-cohort FORCe run

Earlier all-participant FORCe visual review. This is separate from the primary no-FORCe decoder analysis.

**Scope:** 25 available participants.
**Status:** Historical.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/PRE_preprocessing_artifacts/PRE_06_force_full_cohort)

## Inputs and dependencies

PRE_01 and historical FORCe configuration.

- [PRE_01 workflow](../PRE_01_no_force_reference/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

The original stages are shared entry points, rather than copied implementations. Read the [original pipeline instructions](../../../original_pipeline/README_pipeline.md).

```matlab
addpath('Code', 'Code/original_pipeline')
cfg = config('PRE_06');
stage01_parse_events
% For historical processing/plotting, see the precautions in the shared README.
```

The existing PRE_01 reference is protected against overwrite by stage 2. For other IDs, stage 2 recomputes selected outputs. Historical FORCe code has changed since some saved runs; the current library and a parameter profile alone cannot reproduce every historical numerical result. Use saved outputs for those comparisons.

## Settings and numerical interpretation

Read saved settings and the methods in the associated report. The saved configuration inside historical MAT files is provenance; it may retain the original filesystem paths. Scripts resolve current paths when loading those files.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/PRE_preprocessing_artifacts/PRE_06_force_full_cohort). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/PRE_preprocessing_artifacts/report/index.html) · [Report files](../../../../output/PRE_preprocessing_artifacts/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
