# DEC — Decoding and classification

Can displaced versus non-displaced trials be decoded on held-out recording runs, and how do feature designs and classifiers compare?

[Experiment registry](../../../EXPERIMENTS.md) · [Interactive report](../../../output/DEC_decoding/report/index.html)

## Experiments

| ID | Analysis | Scope | Results |
|---|---|---|---|
| [DEC_01](#dec_01) | Pilot decoders | mle01 and spe30; matched trials | [Open](../../../output/DEC_decoding/DEC_01_pilot_decoders/) |
| [DEC_02](#dec_02) | Full-cohort decoders | 25 participants available; 23 non-pilots analysed separately | [Open](../../../output/DEC_decoding/DEC_02_full_cohort_decoders/) |
| [DEC_03](#dec_03) | Graz-style feature comparison | Same evaluated trials and run folds as DEC_02 | [Open](../../../output/DEC_decoding/DEC_03_graz_comparison/) |

## Shared conventions

EEG is sampled at 500 Hz across P3, PO3, PO7, CP5, CP1, Cz, FCz and FC1. Raw voltages are converted from nV to µV. Labels 1/2 mean non-displaced/Correct and displaced/Error. Error − Correct is displaced minus non-displaced; these names do not verify an error percept.

Run commands from the repository root. MATLAB analysis uses Signal Processing Toolbox and, where needed, Statistics and Machine Learning Toolbox. Executing FORCe also requires Wavelet Toolbox and the supplied Windows x64 binaries. Install Python dependencies using `python -m pip install -r requirements-analysis.txt`.

The predefined response interval is [0.2,0.9) s. Channel sets are Central (Cz/FCz), Centroparietal (CP1/CP5), Posterior (P3/PO3/PO7) and Full (all eight). There are 7 bins per channel at 100 ms and 14 at 50 ms. Raw sample features retain 350 values per channel.

Fixed LDA: training-fold standardisation followed by shrinkage LDA (`solver="lsqr"`, `shrinkage="auto"`, equal class priors). Trees use explicitly recorded CART settings. Standardisation, model fitting and supervised ranking are training-only. Whole-run holdouts are within participant/session; this is not transfer of a trained model to an unseen participant.

Balanced accuracy is the mean D/ND recall. Participant results average eligible sessions equally. Pilots are reported separately from the remaining 23 participants. Permutation significance inference is pending.

## DEC_01

**Pilot decoders.** Compare shrinkage LDA channel sets, 100/50 ms bins and samples across four processing conditions; include the pilot tree comparison.

**Scope:** mle01 and spe30; matched trials.

| Step | Script | Operation |
|---|---|---|
| 1 | [export_central_features.m](DEC_01_pilot_decoders/export_central_features.m) | Export Cz/FCz and all-eight-channel matched feature arrays. |
| 2 | [analyse_classification.py](DEC_01_pilot_decoders/analyse_classification.py) | Fit fixed central LDA for 100 ms, 50 ms and sample-wise features. |
| 3 | [summarise_classification.py](DEC_01_pilot_decoders/summarise_classification.py) | Summarise central LDA results. |
| 4 | [analyse_channel_sets.py](DEC_01_pilot_decoders/analyse_channel_sets.py) | Compare every candidate channel set, reusing central predictions. |
| 5 | [analyse_decision_tree.py](DEC_01_pilot_decoders/analyse_decision_tree.py) | Compare the central 100 ms tree with matched saved LDA. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/DEC_decoding/DEC_01_pilot_decoders')
export_central_features
```

```text
python Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_classification.py
python Code/analyses/DEC_decoding/DEC_01_pilot_decoders/summarise_classification.py
python Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_channel_sets.py
python Code/analyses/DEC_decoding/DEC_01_pilot_decoders/analyse_decision_tree.py
```

The pilot uses the four-condition common-trial intersection. Channel/resolution comparisons are exploratory and motivate the fixed configuration evaluated in DEC_02.

[Saved numerical results and figures](../../../output/DEC_decoding/DEC_01_pilot_decoders/).

## DEC_02

**Full-cohort decoders.** Evaluate fixed all-eight-channel LDA, central LDA and an all-channel tree on held-out runs within each participant/session.

**Scope:** 25 participants available; 23 non-pilots analysed separately.

| Step | Script | Operation |
|---|---|---|
| 1 | [prepare_features.m](DEC_02_full_cohort_decoders/prepare_features.m) | Reuse accepted PRE_01 epochs and check the complete three-second raw context. |
| 2 | [evaluate_full_cohort.py](DEC_02_full_cohort_decoders/evaluate_full_cohort.py) | Fit the three fixed decoders with whole-run holdouts; also calls the result summariser. |
| 3 | [summarise_results.py](DEC_02_full_cohort_decoders/summarise_results.py) | Regenerate summary tables/figures from saved metrics without refitting. |
| 4 | [build_figures_tables.py](DEC_02_full_cohort_decoders/build_figures_tables.py) | Build classification-note figures and tables from saved DEC_01/02/03 results. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders')
prepare_features
```

```text
python Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/evaluate_full_cohort.py
python Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/summarise_results.py
python Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/build_figures_tables.py
```

All no-FORCe accepted trials are eligible after full three-second raw-quality checks; FORCe acceptance is irrelevant. Two participant/sessions lack valid classification folds and remain documented in the numerical results. This inclusion set differs slightly from DEC_01’s matched pilot intersection. The note builder also reads DEC_03 results, so run it after that comparison.

[Saved numerical results and figures](../../../output/DEC_decoding/DEC_02_full_cohort_decoders/).

## DEC_03

**Graz-style feature comparison.** Compare a tree with 100 training-selected r-squared amplitudes against predefined binned channel sets.

**Scope:** Same evaluated trials and run folds as DEC_02.

| Step | Script | Operation |
|---|---|---|
| 1 | [prepare_graz_features.m](DEC_03_graz_comparison/prepare_graz_features.m) | Export accepted full-epoch amplitudes for the exact DEC_02 trial IDs. |
| 2 | [analyse_graz_comparison.py](DEC_03_graz_comparison/analyse_graz_comparison.py) | Select 100 features within each training fold and evaluate the matched tree designs. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/DEC_decoding/DEC_03_graz_comparison')
prepare_graz_features
```

```text
python Code/analyses/DEC_decoding/DEC_03_graz_comparison/analyse_graz_comparison.py
```

Uses the exact DEC_02 evaluated trial IDs and folds. The full [-1,+1) s raw-amplitude pool is an explicit interpretation of the Graz methods; the publication does not specify a distinct classifier candidate interval or tree hyperparameters. This is a same-cohort exploratory follow-up, not an independent new test set.

[Saved numerical results and figures](../../../output/DEC_decoding/DEC_03_graz_comparison/).

## Research note

The category report folder contains the interactive HTML overview, formal PDF and editable LaTeX. The reviewed LaTeX is the authoritative manuscript source. To rebuild the HTML overviews from saved results: `python Code/helpers/build_web_reports.py`.
