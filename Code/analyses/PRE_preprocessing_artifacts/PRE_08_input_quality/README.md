# PRE_08: Input-quality screen

Characterise suspected input contamination in one-second windows before reviewing cleaner outputs.

**Scope:** Two pilots; all eight channels.
**Status:** Completed; expert assessment remains separate.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/PRE_preprocessing_artifacts/PRE_08_input_quality)

## Inputs and dependencies

PRE_01 parsed metadata and raw recordings.

- [PRE_01 workflow](../PRE_01_no_force_reference/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [run_input_screen.m](run_input_screen.m) — Screen raw/continuous-high-pass inputs in one-second windows.
2. [summarise_inputs.py](summarise_inputs.py) — Summarise flag prevalence and review selection.
3. [plot_input_review.m](plot_input_review.m) — Draw the input-only review examples.
4. [finish_review.m](finish_review.m) — Complete the saved review illustrations and target-aligned summaries.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/PRE_preprocessing_artifacts/PRE_08_input_quality')
run_input_screen.m
plot_input_review.m
finish_review.m
```

Python entry scripts (follow the numbered order above):

```text
.venv/Scripts/python.exe Code/analyses/PRE_preprocessing_artifacts/PRE_08_input_quality/summarise_inputs.py
```

## Settings and numerical interpretation

Read saved settings and the methods in the associated report. The saved configuration inside historical MAT files is provenance; it may retain the original filesystem paths. Scripts resolve current paths when loading those files.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/PRE_preprocessing_artifacts/PRE_08_input_quality). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/PRE_preprocessing_artifacts/report/index.html) · [Report files](../../../../output/PRE_preprocessing_artifacts/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
