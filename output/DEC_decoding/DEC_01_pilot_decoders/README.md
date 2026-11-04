# Displaced versus non-displaced classification pilot

## What was tested

Fixed shrinkage LDA using Cz and FCz over **[0.2, 0.9) s**, separately for each participant and session. The three representations are seven 100 ms means/channel (14 features), fourteen 50 ms means/channel (28 features), and all 350 original 500 Hz samples/channel (700 features). Every representation uses the same interval. No samples were downsampled for the original-sample representation.

| ID | Processing condition |
|---|---|
| 1 | BP no-FORCe |
| 2 | BP FORCe |
| 3 | Split no-FORCe |
| 4 | Split FORCe |

Conditions 1/2 use continuous 1–20 Hz bandpass filtering; 2 then applies FORCe to three one-second windows. Conditions 3/4 use continuous 1 Hz high-pass filtering followed by a 20 Hz low-pass on the three-second segment; 4 applies FORCe to three one-second windows before that low-pass. All use the saved, cropped two-second epochs, identical baseline correction, and FORCe window boundaries at −0.5 and +0.5 s in conditions 2/4. The feature interval therefore includes the +0.5 s boundary. This test uses these saved conditions; it does not test the historical two-window join at onset.

## Validation and trial matching

- 2,562 trial IDs accepted in all four conditions; no new input-flag exclusions. Original label 1 means non-displaced (ND); label 2 means displaced (D). D is the positive classification class.
- Each participant/session is analysed independently. Leave one complete recording run out; the other runs train the model. No run is shared by training and test sets.
- Five folds per participant/session, except spe30/retest: four available runs (1, 3, 4, 5). All configurations use identical held-out trial IDs.
- Model: training-fold StandardScaler, then LDA with solver="lsqr", shrinkage="auto" and equal class priors [0.5, 0.5]. No tuning, feature selection, threshold search or resampling. Shrinkage is estimated using training data only. Decision score > 0 predicts D.
- 348 fitted models; 30,744 predictions. Every trial receives exactly one held-out prediction per condition/representation.

This tests generalisation to another run **within the same participant/session**, not to an unseen session or participant. The pilot data have already informed the channel and interval choices; these are exploratory results.

## Metrics

**Balanced accuracy (BA)** = (D sensitivity + ND specificity)/2, computed from the pooled out-of-fold confusion counts within each participant/session. **Primary ROC-AUC** is the unweighted mean of the held-out-run AUCs: separate fitted folds may have different score scales. The pooled OOF AUC is also saved as a secondary metric. A constant majority classifier has BA and AUC 0.5. This is a chance reference, not a significance threshold.

The run-variability figure shows each held-out-run BA and its arithmetic mean, which can differ from pooled OOF BA when run/class counts differ. Ranges across runs are descriptive, not confidence intervals. No population significance tests are made.

## Primary no-FORCe results

Each cell below is **BA / mean-run AUC** for condition 1.

| Participant / session | ND / D | Runs | 100 ms | 50 ms | Samples |
|---|---:|---:|---:|---:|---:|
| mle01 / pre | 309 / 166 | 5 | 0.676 / 0.712 | 0.671 / 0.696 | 0.648 / 0.713 |
| mle01 / post | 218 / 114 | 5 | 0.695 / 0.703 | 0.657 / 0.709 | 0.700 / 0.717 |
| mle01 / retest | 237 / 132 | 5 | 0.796 / 0.837 | 0.775 / 0.840 | 0.753 / 0.818 |
| spe30 / pre | 326 / 169 | 5 | 0.842 / 0.918 | 0.830 / 0.915 | 0.813 / 0.905 |
| spe30 / post | 329 / 169 | 5 | 0.827 / 0.900 | 0.834 / 0.923 | 0.848 / 0.913 |
| spe30 / retest | 260 / 133 | 4 | 0.654 / 0.713 | 0.593 / 0.641 | 0.605 / 0.643 |

## Comparison of all conditions

Below are unweighted descriptive means across the six participant/session results. They are not six independent participants or an estimate of population performance.

| Condition | Representation | Mean BA | Mean run-AUC | D sensitivity | ND specificity |
|---|---|---:|---:|---:|---:|
| BP no-FORCe | 100ms | 0.748 | 0.797 | 0.748 | 0.748 |
| BP no-FORCe | 50ms | 0.727 | 0.787 | 0.708 | 0.745 |
| BP no-FORCe | samples | 0.728 | 0.785 | 0.691 | 0.764 |
| BP FORCe | 100ms | 0.685 | 0.738 | 0.688 | 0.683 |
| BP FORCe | 50ms | 0.694 | 0.738 | 0.680 | 0.708 |
| BP FORCe | samples | 0.680 | 0.731 | 0.634 | 0.727 |
| Split no-FORCe | 100ms | 0.746 | 0.797 | 0.745 | 0.747 |
| Split no-FORCe | 50ms | 0.728 | 0.787 | 0.709 | 0.747 |
| Split no-FORCe | samples | 0.727 | 0.784 | 0.688 | 0.765 |
| Split FORCe | 100ms | 0.682 | 0.744 | 0.680 | 0.684 |
| Split FORCe | 50ms | 0.685 | 0.739 | 0.672 | 0.697 |
| Split FORCe | samples | 0.684 | 0.735 | 0.646 | 0.722 |

## Interpretation

- **100 ms bins remain a sensible first baseline.** In the primary condition, they give the highest BA in four of six participant/sessions; original samples give the highest BA in two. 50 ms bins have no consistent advantage. The six-session mean BA favours 100 ms, with far fewer features than the original samples. This supports a practical starting point, not a universal optimal bin width.
- **The two no-FORCe controls are similar:** the largest absolute BA difference between conditions 3 and 1 is 1.11 percentage points across the 18 participant/session/representation comparisons.
- **FORCe does not improve classification consistently:** BP FORCe has lower BA than its matched BP control in 17/18 comparisons; split FORCe has lower BA than its split control in 18/18. These are descriptive comparisons of related results, not independent statistical tests.
- **Session differences remain:** spe30/retest is weaker than spe30/pre and post. The held-out-run figure shows substantial run variability, so a single pooled pilot score would hide useful differences.
- These findings support continuing with no-FORCe as the primary working analysis and 100 ms Cz/FCz features as a compact baseline, while retaining 50 ms and original-sample results as sensitivities. They do not establish that FORCe removes useful neural activity: better prediction can also exploit contamination or other class-related differences. Likewise, predictive class information alone does not identify a neural ErrP component.
- The next independent question would be how this fixed baseline transfers to other sessions or participants. That was not tested here.

## Files and reproduction

- `export_central_features.m`: extracts matched Cz/FCz data from saved epochs; verifies the 100 ms features against the prior feature audit.
- `analyse_classification.py`: fits the fixed models and verifies matching and OOF coverage.
- `summarise_classification.py`: builds this summary and the plots from saved scores.
- `trial_metadata.csv`: original recording/run/trial IDs and labels.
- `session_metrics.csv`: all 72 participant/session/configuration summaries and confusion counts.
- `fold_metrics.csv`: all 348 held-out-run scores and training/test class counts.
- `heldout_predictions.csv`: 30,744 individual held-out predictions and decision scores.
- `paired_fold_differences.csv` and `paired_comparison_summary.csv`: identical-fold comparisons for FORCe, filtering, and temporal representation.
- `descriptive_pilot_summary.csv`: six-session descriptive means.
- `analysis_settings.json` and `requirements.txt`: model settings, checks and package versions.
- `figures/classification_scores.png`: all session scores; `heldout_run_variability.png`: individual folds; `class_specific_scores.png`: class-specific recalls. Vector PDF copies are also saved for reuse in a later research note.

From the repository root, run the export with MATLAB, then run the two Python scripts in the recorded environment. The local `.venv`, exported MAT data and temporary files are ignored. Existing pipeline outputs and earlier research notes are preserved.

Method references: [scikit-learn LDA](https://scikit-learn.org/stable/modules/generated/sklearn.discriminant_analysis.LinearDiscriminantAnalysis.html), [leave-one-group-out](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneGroupOut.html).


## Decision-tree follow-up

The [Graz-style decision-tree comparison](decision_tree/README.md) applies the same 14 binned Cz/FCz features to the primary no-FORCe data, using identical whole-run holdouts. It preserves the LDA results above and documents the assumptions needed because the paper does not specify the tree hyperparameters. Run `analyse_decision_tree.py` after this analysis.

## All audited channel sets

The [expanded LDA comparison](channel_sets/README.md) uses Central, Centroparietal, Posterior and Full channel sets, with the same three temporal representations, four processing conditions and held-out runs. Run the extended `export_central_features.m`, then `analyse_channel_sets.py`. Original Central results are reused; the other three channel groups are fitted with the same shared LDA settings.


[Current workflow and scripts](../../../Code/analyses/DEC_decoding/DEC_01_pilot_decoders/README.md)
