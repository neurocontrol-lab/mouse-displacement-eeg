# DEC_01: Pilot decoders

Compare shrinkage LDA channel sets, 100/50 ms bins and samples across four processing conditions; include the pilot tree comparison.

**Scope:** mle01 and spe30; matched trials.
**Status:** Completed; exploratory selection.

[Experiment registry](../../../../EXPERIMENTS.md) · [Saved results](../../../../output/DEC_decoding/DEC_01_pilot_decoders)

## Inputs and dependencies

FEA_01 audit and PRE_09 matched trial IDs.

- [FEA_01 workflow](../../FEA_features_repeatability/FEA_01_feature_audit/README.md)

- [PRE_09 workflow](../../PRE_preprocessing_artifacts/PRE_09_retention_and_erp/README.md)

Raw EEG is converted from nV to µV. Labels are 1 = non-displaced (Correct), 2 = displaced (Error). Error − Correct means displaced minus non-displaced; these labels do not establish an independently verified error percept.

## Workflow and execution

Run from the repository root. MATLAB needs Signal Processing Toolbox; FORCe execution additionally needs Wavelet Toolbox and the supplied Windows x64 MEX files. Statistical scripts may require Statistics and Machine Learning Toolbox. Python dependencies are in `requirements-analysis.txt` at the root.

1. [export_central_features.m](export_central_features.m) — Export Cz/FCz and all-eight-channel matched feature arrays.
2. [analyse_classification.py](analyse_classification.py) — Fit fixed central LDA for 100 ms, 50 ms and sample-wise features.
3. [summarise_classification.py](summarise_classification.py) — Summarise central LDA results.
4. [analyse_channel_sets.py](analyse_channel_sets.py) — Compare every candidate channel set, reusing central predictions.
5. [analyse_decision_tree.py](analyse_decision_tree.py) — Compare the central 100 ms tree with matched saved LDA.

MATLAB entry scripts (follow the mixed MATLAB/Python order above):

```matlab
addpath('Code')
addpath('Code/analyses/DEC_decoding/DEC_01_pilot_decoders')
export_central_features.m
```

Python entry scripts (follow the numbered order above):

```text
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_classification.py
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_01_pilot_decoders/summarise_classification.py
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_channel_sets.py
.venv/Scripts/python.exe Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_decision_tree.py
```

## Settings and numerical interpretation

The response feature interval is [0.2, 0.9) s. Channel sets are Central (Cz/FCz), Centroparietal (CP1/CP5), Posterior (P3/PO3/PO7), and Full (all eight). Standardisation, model fitting and any supervised selection use training folds only. Run holdouts are within participant/session; this is not a classifier-transfer evaluation across participants.

LDA uses `StandardScaler` then `LinearDiscriminantAnalysis(solver="lsqr", shrinkage="auto", priors=[0.5,0.5])`. Tree defaults and sampling settings are explicit in the scripts and saved `analysis_settings.json`. Balanced accuracy is the mean D/ND recall. Participant summaries average eligible sessions equally. Pilot and non-pilot cohorts are reported separately.

No permutation significance test has been added by this refactor. Scores above 50% are observed scores until inference is performed. The Graz-style selection is an interpretation of the publication, not an exact reproduction of its validation.

## Outputs and reports

Numerical outputs, configuration snapshots and figures are in [the result folder](../../../../output/DEC_decoding/DEC_01_pilot_decoders). Intermediate MAT caches are local; raw data and caches are not required to browse the HTML/PDF summaries.

[Category HTML report](../../../../output/DEC_decoding/report/index.html) · [Report files](../../../../output/DEC_decoding/report)

The reviewed LaTeX is authoritative. Retired full-manuscript generators are archived locally; do not regenerate reviewed prose from an earlier builder.
