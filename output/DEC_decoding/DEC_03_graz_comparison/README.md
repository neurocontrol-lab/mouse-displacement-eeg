# Graz-style amplitude selection versus our decision-tree feature sets

## What the paper specifies

The Graz paper reports movement-locked epochs spanning [−1,+1] s, a binary decision tree, and 100 channel/time-point amplitude features ranked by r-squared using each fold's training data. It does **not** state that classification was restricted to [0.2,0.9) s. Nor does it separately state the precise classification candidate interval. Using all samples in its documented two-second epoch is therefore our explicit full-epoch interpretation, not a recovered implementation detail.

The 100 features are 100 **channel/time-point pairs**. They need not represent 100 unique clock times, and they are not time-bin averages.

## Matched comparison

| Tree feature design | Candidate pool | Inputs to tree |
|---|---|---:|
| Graz-style full epoch | 8 channels × 1000 samples, [−1,+1) s | Training-fold top 100 |
| Same-interval amplitude control | 8 channels × 350 samples, [0.2,0.9) s | Training-fold top 100 |
| Central bins: Cz, FCz | Seven 100 ms means/channel, [0.2,0.9) s | 14 |
| Centroparietal bins: CP1, CP5 | Same seven bins/channel | 14 |
| Posterior bins: P3, PO3, PO7 | Same seven bins/channel | 21 |
| Full montage bins | Same seven bins, all eight channels | 56 |

R-squared is squared Pearson correlation with the binary class label, matching `Code/reference/rsquared.m`. Constant features receive zero, consistent with the legacy classifier's undefined-score handling. Feature ranking is recomputed from training trials separately in every fold; the test recording does not influence ranking, means or thresholds. Ties use fixed channel/time order. An independent Pearson calculation checks the vectorised ranking implementation.

All six designs use the exact accepted no-FORCe trial IDs, existing session eligibility decisions and whole-recording holdouts from the full-dataset analysis. All use the same fixed Gini CART settings, no pruning or class weighting and random seed 20261027. There is no tuning. The Full-bin tree predictions are reused exactly; the other five designs are new fits. This isolates the feature-design comparison within a fixed tree/evaluation setup.

There are 30,210 evaluated trials across 73 participant/sessions, 2,094 comparison folds, 1,745 new tree fits, 349 reused Full-bin folds and 181,260 held-out predictions. The 23 validation participants are reported separately from the two pilots. The two previously excluded pre sessions remain excluded; no new trial filtering or preprocessing is performed.

## Validation results

Metrics are averaged across eligible sessions within each participant, then participants equally. Session BA uses all held-out confusion counts; AUC averages defined two-class held-out-run AUCs.

| Feature design | Accuracy | BA | D sensitivity | ND specificity | AUC |
|---|---:|---:|---:|---:|---:|
| Top 100 r²: −1 to +1 s | 0.653 | 0.617 | 0.505 | 0.728 | 0.618 |
| Top 100 r²: 0.2–0.9 s | 0.649 | 0.612 | 0.498 | 0.726 | 0.614 |
| 100 ms: Central | 0.677 | 0.644 | 0.544 | 0.744 | 0.645 |
| 100 ms: Centroparietal | 0.670 | 0.636 | 0.532 | 0.739 | 0.636 |
| 100 ms: Posterior | 0.671 | 0.636 | 0.533 | 0.739 | 0.636 |
| 100 ms: Full | 0.692 | 0.659 | 0.561 | 0.757 | 0.659 |

The [previous full-dataset LDA results](../DEC_02_full_cohort_decoders/README.md) remain unchanged. The comparison figure includes their full-montage mean as a reference; class handling differs between that LDA and these trees.

## Pilot results, separate

| Feature design | BA | AUC |
|---|---:|---:|
| Top 100 r²: −1 to +1 s | 0.631 | 0.629 |
| Top 100 r²: 0.2–0.9 s | 0.629 | 0.627 |
| 100 ms: Central | 0.713 | 0.712 |
| 100 ms: Centroparietal | 0.698 | 0.693 |
| 100 ms: Posterior | 0.674 | 0.668 |
| 100 ms: Full | 0.700 | 0.701 |

## Interpretation

- Compare full-epoch and response-interval r-squared models to assess the candidate-interval choice under the same selection rule. The response-interval r-squared control and our bins share [0.2,0.9), allowing a closer feature-method comparison. The number of inputs still differs: 100 selected amplitudes versus 14–56 bin means.
- This is a Graz-style feature-selection and classifier comparison, not an exact reproduction of its published scores. We retain no-FORCe preprocessing, a fourth-order filter, session-specific whole-run holdouts and explicit tree defaults. The paper used FORCe, a third-order filter and reported 10-fold CV; tree hyperparameters were not specified.
- Models remain personalised. This does not test transfer of a trained model to another participant/session or establish a neural ErrP source. Results are descriptive; no new hyperparameters are chosen from these scores.
- Selected samples can be adjacent and strongly correlated. Selection frequency across overlapping training folds is not independent evidence for a component latency or cortical source. Full-epoch features can include pre-onset samples.
- These additional feature designs are follow-up exploratory comparisons on the same validation cohort; their results do not create a new untouched test set.

## Files and reproduction

- `cohort_summary.csv`, `participant_metrics.csv`, `session_metrics.csv`, `fold_metrics.csv`: results at each level.
- `heldout_predictions.csv`: all six designs with identical trial/label IDs.
- `selected_features.csv`: each selected channel, time, rank and training r-squared for both raw-amplitude models, separately for every held-out run.
- `paired_participant_differences.csv`: differences from the Full-bin tree.
- `analysis_settings.json`: exact assumptions, settings and verification.
- `feature_design_comparison.png`: participant-wise and mean validation scores.


Source: [Graz paper, Data Analysis and Evaluation](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf).


[Current workflow and scripts](../../../Code/analyses/DEC_decoding/README.md#dec_03)

[Methods, settings and execution order](../../../Code/analyses/DEC_decoding/README.md#dec_03)
