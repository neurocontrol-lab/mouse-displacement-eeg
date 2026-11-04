# DEC_03: Graz-style feature comparison

Compare a tree with 100 training-selected r-squared amplitudes against predefined binned channel sets.

**Scope:** Same evaluated trials and run folds as DEC_02.
**Status:** Completed; exploratory feature follow-up.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/DEC_decoding/DEC_03_graz_comparison)

## Inputs and dependencies

DEC_02; PRE_01 full epochs.

- [DEC_02 workflow](../DEC_02_full_cohort_decoders/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [prepare_graz_features.m](prepare_graz_features.m) — Export accepted full-epoch amplitudes for the exact DEC_02 trial IDs.
2. [analyse_graz_comparison.py](analyse_graz_comparison.py) — Select 100 features within each training fold and evaluate the matched tree designs.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/DEC_decoding/DEC_03_graz_comparison')
prepare_graz_features.m
```

Python entry scripts (follow the numbered order above):

```text
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_03_graz_comparison/analyse_graz_comparison.py
```

## Settings and numerical interpretation

The response feature interval is [0.2, 0.9) s. Channel sets are Central (Cz/FCz), Centroparietal (CP1/CP5), Posterior (P3/PO3/PO7), and Full (all eight). Standardisation, model fitting and any supervised selection use training folds only. Run holdouts are within participant/session; this is not a classifier-transfer evaluation across participants.

LDA uses `StandardScaler` then `LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto", priors=[0.5,0.5])`. Tree defaults and sampling settings are explicit in the scripts and saved `analysis_settings.json`. Balanced accuracy is the mean D/ND recall. Participant summaries average eligible sessions equally. Pilot and non-pilot cohorts are reported separately.

No permutation significance test has been added by this refactor. Scores above 50% are observed scores until inference is performed. The Graz-style selection is an interpretation of the publication, not an exact reproduction of its validation.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/DEC_decoding/DEC_03_graz_comparison). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/DEC_decoding/report/index.html) · [Report files](../../../../output/DEC_decoding/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
