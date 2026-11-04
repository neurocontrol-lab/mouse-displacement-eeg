# Fixed-decoder evaluation across the available dataset

## Scope and protocol

The available dataset contains 25 participants. The two decoder-selection pilots, mle01 and spe30, are reported separately. The remaining 23 participants assess the fixed configurations chosen during that pilot; this is internal validation, not an external cohort or a test of cross-participant model transfer. Each model is trained on other runs of the same participant and session.

| Decoder | Channels | Features |
|---|---|---:|
| Shrinkage LDA | All eight | 56 |
| Shrinkage LDA | Cz, FCz | 14 |
| Binary decision tree | All eight | 56 |

Each channel contributes seven non-overlapping 100 ms mean amplitudes over **[0.2, 0.9) s**. The montage is P3, PO3, PO7, CP5, CP1, Cz, FCz and FC1. All three decoders use identical accepted trial IDs and identical leave-one-complete-recording-out folds, separately for pre, post and retest. There is no hyperparameter search, feature ranking, threshold tuning or resampling.

LDA uses training-fold StandardScaler, solver="lsqr", shrinkage="auto" and equal class priors [0.5,0.5]. The tree uses Gini impurity, best binary splits, unrestricted depth, minimum leaf size 1, no pruning, equal sample weights, and seed 20261027. These explicit tree defaults approximate the Graz classifier family; its precise hyperparameters were not reported. Class handling differs between the configured LDA and tree. This experiment does not reproduce the paper's 100 r-squared-selected features or 10-fold validation.

## Preprocessing and data inclusion

Filtering and final two-second epoch values are reused from saved PRE_01: continuous fourth-order 1–20 Hz Butterworth filtering with filtfilt, movement alignment, baseline correction over [−0.2,0) s, and rejection above 100 microvolts absolute amplitude across the complete two-second epoch and all eight channels. No FORCe or other reconstructive artifact removal is used. The exporter checks the stored settings.

Raw loss codes, timestamp gaps and nonfinite EEG are checked over the complete [−1.5,1.5) s interval, with the same two-second valid-segment edge guards as the recent pilot. No labels or exclusions are revised after seeing classification results. All trials passing this no-FORCe pipeline are included; acceptance by any FORCe condition is irrelevant. The full signal and acceptance checks against the saved pilot controls are in `pilot_cache_verification.csv`.

There are 380 inventoried recordings and 30,231 accepted trials. 30,210 accepted trials enter the evaluable sessions. Recordings with no valid events and trials that fail quality checks remain in the inventory and retention tables.

A session needs at least two recording runs with accepted trials and both classes in every training fold. A single-class test fold still receives predictions; its run AUC and run BA are undefined. The session BA uses all its held-out predictions and both class totals. AUC averages only defined, two-class held-out-run AUCs; their number is recorded.

Original labels: 1 = non-displaced (binary 0), 2 = displaced (binary 1). Sensitivity concerns displaced trials; specificity concerns non-displaced trials.

## Primary validation results

**Participant weighting:** first average each metric across eligible sessions within a participant, then average participants equally. The table is not weighted by trial counts. Session BA comes from pooled out-of-fold class recalls; session AUC is the mean of defined held-out-run AUCs.

| Decoder | Participants | Sessions | Accuracy | BA | D sensitivity | ND specificity | AUC |
|---|---:|---:|---:|---:|---:|---:|---:|
| LDA, all eight | 23 | 67 | 0.770 | 0.763 | 0.744 | 0.782 | 0.822 |
| LDA, Cz/FCz | 23 | 67 | 0.708 | 0.703 | 0.690 | 0.717 | 0.756 |
| Decision tree, all eight | 23 | 67 | 0.692 | 0.659 | 0.561 | 0.757 | 0.659 |

Full-montage LDA has higher participant-mean BA in 22/23 validation participants (0 ties). Its participant-weighted mean difference from Central is +5.96 percentage points. This is a descriptive paired comparison, not a population significance test.

## Pilot results, kept separate

| Decoder | Participants | Sessions | Accuracy | BA | AUC |
|---|---:|---:|---:|---:|---:|
| LDA, all eight | 2 | 6 | 0.804 | 0.808 | 0.859 |
| LDA, Cz/FCz | 2 | 6 | 0.747 | 0.747 | 0.797 |
| Decision tree, all eight | 2 | 6 | 0.732 | 0.700 | 0.701 |

These pilot models are refitted on all accepted no-FORCe trials. Their scores can differ from the earlier four-condition matched pilot because the acceptance intersection and training trial counts have changed.

## Sessions excluded from cross-validation

| Participant / session | Accepted trials | Accepted recordings | Reason |
|---|---:|---:|---|
| rle13 / pre | 10 | 1 | fewer_than_two_accepted_recordings |
| vco27 / pre | 11 | 2 | a_training_fold_has_only_one_class |

## Interpretation limits

- This evaluates personalised decoders on held-out recording runs. Models do not transfer from other participants or sessions. Validation participants were outside this two-participant decoder-selection pilot; previous exploratory work on the dataset means this should not be described as a blinded external test.
- A full-montage advantage does not localise the source of predictive information. The additional channels include FC1 as well as centroparietal/posterior electrodes.
- Better prediction does not establish that the signal is specifically a neural ErrP or that accepted epochs are artifact-free. The no-FORCe acceptance rules remain the existing quality-control baseline.
- The unpruned tree may give pure-leaf probabilities of 0/1, so its within-run AUC can equal BA. LDA and tree score ranges and class handling differ. No settings are changed in response to these results.
- Participants with an excluded session are averaged over their remaining eligible sessions; session-level results and retention counts expose this coverage.

## Outputs and reproduction

- `cohort_summary.csv`: equal-participant validation and separate pilot summaries.
- `participant_metrics.csv`, `session_metrics.csv`, `fold_metrics.csv`: all evaluation levels.
- `heldout_predictions.csv`: individual test predictions, original trial IDs and scores.
- `paired_participant_differences.csv`: paired decoder differences.
- `trial_quality.csv`, `retention_by_run.csv`, `retention_by_session.csv`, `rejection_counts.csv`: complete inclusion and rejection accounting.
- `session_eligibility.csv`: why any session cannot support the fixed evaluation.
- `analysis_settings.json`: exact frozen model and preprocessing settings.
- `figures/validation_participant_scores.png`: participant-wise BA and AUC.
- `figures/validation_session_scores.png`: separate session results for all models.


Reference: [Graz paper](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf).

## Graz-style tree feature comparison

The [matched decision-tree feature comparison](../DEC_03_graz_comparison/README.md) adds 100 training-fold r-squared-selected channel/time amplitudes from the full epoch, a same-interval 0.2–0.9 s control, and trees using the four audited channel sets. It preserves the results above and documents the paper's unspecified classifier interval and tree settings.

## Research note

The consolidated [D/ND classification research note](../report/D_ND_classification_research_note.pdf) covers the matched pilot, fixed full-dataset evaluation and Graz-style tree feature comparison. Its editable LaTeX project is in `../classification_note/`.


[Current workflow and scripts](../../../Code/analyses/DEC_decoding/README.md#dec_02)

[Methods, settings and execution order](../../../Code/analyses/DEC_decoding/README.md#dec_02)
