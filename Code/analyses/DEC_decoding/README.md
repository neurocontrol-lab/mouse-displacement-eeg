# DEC — Decoding and classification

Can displaced versus non-displaced trials be decoded on held-out recording runs, and how do feature designs and classifiers compare?

[Experiment registry](../../../EXPERIMENTS.md) · [Interactive report](../../../output/DEC_decoding/report/index.html)

## Experiments

| ID | Analysis | Scope | Results |
|---|---|---|---|
| [DEC_01](#dec_01) | Pilot decoders | mle01 and spe30; matched trials | [Open](../../../output/DEC_decoding/DEC_01_pilot_decoders/) |
| [DEC_02](#dec_02) | Full-cohort decoders | 25 participants available; 23 non-pilots analysed separately | [Open](../../../output/DEC_decoding/DEC_02_full_cohort_decoders/) |
| [DEC_03](#dec_03) | Graz-style feature comparison | Same evaluated trials and run folds as DEC_02 | [Open](../../../output/DEC_decoding/DEC_03_graz_comparison/) |
| [DEC_04](#dec_04) | Within-run permutation inference | Fixed four-model comparison; 23 non-pilots and two exploratory pilots | [Open](../../../output/DEC_decoding/DEC_04_permutation_inference/) |

## Shared conventions

EEG is sampled at 500 Hz across P3, PO3, PO7, CP5, CP1, Cz, FCz and FC1. Raw voltages are converted from nV to µV. Labels 1/2 mean non-displaced/Correct and displaced/Error. Error − Correct is displaced minus non-displaced; these names do not verify an error percept.

Run commands from the repository root. MATLAB analysis uses Signal Processing Toolbox and, where needed, Statistics and Machine Learning Toolbox. Executing FORCe also requires Wavelet Toolbox and the supplied Windows x64 binaries. Install Python dependencies using `python -m pip install -r requirements-analysis.txt`.

The predefined response interval is [0.2,0.9) s. Channel sets are Central (Cz/FCz), Centroparietal (CP1/CP5), Posterior (P3/PO3/PO7) and Full (all eight). There are 7 bins per channel at 100 ms and 14 at 50 ms. Raw sample features retain 350 values per channel.

Fixed LDA: training-fold standardisation followed by shrinkage LDA (`solver="lsqr"`, `shrinkage="auto"`, equal class priors). Trees use explicitly recorded CART settings. Standardisation, model fitting and supervised ranking are training-only. Whole-run holdouts are within participant/session; this is not transfer of a trained model to an unseen participant.

Balanced accuracy is the mean D/ND recall. Participant results average eligible sessions equally. Pilots are reported separately from the remaining 23 participants. DEC_04 evaluates permutation-derived chance thresholds and one-sided p-values for the fixed decoder configurations.

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

## DEC_04

**Within-run permutation inference.** Compare the fixed full LDA, central LDA, full binned tree and full-epoch Graz-style top-100 tree against their label-shuffled nulls. Primary preprocessing is BP no-FORCe; no additional preprocessing conditions are fitted here.

The exact DEC_02 eligible sessions, accepted IDs and whole-run folds are reused. All four observed prediction vectors must reproduce DEC_02/03 before permutations run. For 1,999 shuffles, D/ND labels are permuted independently within each recording, preserving its counts. This assumes within-recording label exchangeability under the null; it does not preserve arbitrary serial label dependence.

All classifiers are refitted for every permutation/fold, with training-only standardisation and reranking of the Graz features. Label-independent raw moments are cached to accelerate the algebraically identical training-only r-squared ranking; unpermuted ranks are checked against the original helper. Every model receives the same shuffled labels. Seeds are deterministic per participant, session and permutation, independent of worker order. Sessions checkpoint every 100 shuffles so a rerun can resume.

Balanced accuracy pools all held-out test predictions within each session, then participant statistics average eligible sessions equally. Null participant scores use that identical aggregation. The one-sided Monte Carlo p-value is `(1 + number(null >= observed))/(1 + permutations)`. The 95th-percentile threshold uses the higher empirical quantile and is unadjusted; Holm p-values determine family-wise corrected significance.

**Families:** 23 primary non-pilot full-LDA tests; a separate family of 69 secondary non-pilot tests (three baselines); and eight exploratory pilot/model tests. Pilot adjustment does not undo selection on those participants. Session-level p-values are unadjusted exploratory checks. The p-value resolution at 1,999 shuffles is 0.0005.

| Step | Script | Operation |
|---|---|---|
| 1, if needed | [prepare_graz_features.m](DEC_03_graz_comparison/prepare_graz_features.m) | Re-export saved full-epoch amplitudes for training-fold selection. |
| 2 | [run_permutations.py](DEC_04_permutation_inference/run_permutations.py) | Reproduce saved predictions, refit the four models under shuffles, save session nulls and participant/session inference tables. |
| 3 | [build_inference_note.py](DEC_04_permutation_inference/build_inference_note.py) | Build the primary LDA note's tables and observed-versus-chance figure from completed inference. |
| 4 | [build_web_reports.py](../../helpers/build_web_reports.py) | Add all baseline inference tables to the existing DEC report. |

```text
python Code/analyses/DEC_decoding/DEC_04_permutation_inference/run_permutations.py --permutations 1999 --workers 4
python Code/analyses/DEC_decoding/DEC_04_permutation_inference/build_inference_note.py
python Code/helpers/build_web_reports.py --category DEC_decoding
```

To regenerate only the inference tables from completed score arrays, use `run_permutations.py --summarise-only`; this does not refit models or require the full-epoch exports.

The editable `D_ND_permutation_significance_note.tex` in the category report folder is compiled with LaTeX after step 3. The compact PDF focuses on full LDA; all four models remain available in the existing web report. Null arrays contain scores, not EEG. These tests establish label-related discrimination conditional on this analysis, not the neural identity of an ErrP.

[Saved inference results](../../../output/DEC_decoding/DEC_04_permutation_inference/).

## Research note

The category report folder contains the interactive HTML overview, formal PDF and editable LaTeX. The reviewed LaTeX is the authoritative manuscript source. To rebuild the HTML overviews from saved results: `python Code/helpers/build_web_reports.py`.
