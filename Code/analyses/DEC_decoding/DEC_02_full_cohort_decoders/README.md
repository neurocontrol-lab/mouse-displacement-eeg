# DEC_02: Full-cohort decoders

Evaluate fixed all-eight-channel LDA, central LDA and an all-channel tree on held-out runs within each participant/session.

**Scope:** 25 participants available; 23 non-pilots analysed separately.
**Status:** Completed; permutation inference pending.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/DEC_decoding/DEC_02_full_cohort_decoders)

## Inputs and dependencies

PRE_01 saved epochs, raw three-second quality checks.

- [PRE_01 workflow](../../PRE_preprocessing_artifacts/PRE_01_no_force_reference/README.md)

- [DEC_01 workflow](../DEC_01_pilot_decoders/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [prepare_features.m](prepare_features.m) — Reuse accepted PRE_01 epochs and check the complete three-second raw context.
2. [evaluate_full_cohort.py](evaluate_full_cohort.py) — Fit the three fixed decoders with whole-run holdouts; also calls the result summariser.
3. [summarise_results.py](summarise_results.py) — Regenerate summary tables/figures from saved metrics without refitting.
4. [build_figures_tables.py](build_figures_tables.py) — Build classification-note figures and tables from saved DEC_01/02/03 results.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders')
prepare_features.m
```

Python entry scripts (follow the numbered order above):

```text
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/evaluate_full_cohort.py
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/summarise_results.py
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/build_figures_tables.py
```

## Settings and numerical interpretation

The response feature interval is [0.2, 0.9) s. Channel sets are Central (Cz/FCz), Centroparietal (CP1/CP5), Posterior (P3/PO3/PO7), and Full (all eight). Standardisation, model fitting and any supervised selection use training folds only. Run holdouts are within participant/session; this is not a classifier-transfer evaluation across participants.

LDA uses `StandardScaler` then `LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto", priors=[0.5,0.5])`. Tree defaults and sampling settings are explicit in the scripts and saved `analysis_settings.json`. Balanced accuracy is the mean D/ND recall. Participant summaries average eligible sessions equally. Pilot and non-pilot cohorts are reported separately.

No permutation significance test has been added by this refactor. Scores above 50% are observed scores until inference is performed. The Graz-style selection is an interpretation of the publication, not an exact reproduction of its validation.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/DEC_decoding/DEC_02_full_cohort_decoders). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/DEC_decoding/report/index.html) · [Report files](../../../../output/DEC_decoding/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
