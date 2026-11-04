# LDA comparison of all audited channel sets

## Fixed analysis

The original shrinkage-LDA comparison is extended to every channel set from the feature audit. All 2,562 matched trial IDs, four processing conditions, three temporal representations and participant/session-specific whole-run holdouts are retained. Condition 1, BP no-FORCe, is the primary analysis. Other conditions are sensitivity comparisons.

| Channel set | Channels | 100 ms features | 50 ms features | Sample features |
|---|---|---:|---:|---:|
| Central | Cz, FCz | 14 | 28 | 700 |
| Centroparietal | CP1, CP5 | 14 | 28 | 700 |
| Posterior | P3, PO3, PO7 | 21 | 42 | 1050 |
| Full | P3, PO3, PO7, CP5, CP1, Cz, FCz, FC1 | 56 | 112 | 2800 |

All representations cover [0.2, 0.9) s. The sample representation uses the original 500 Hz samples. Each channel contributes its own features; no channel averaging is used.

The shared model is training-fold StandardScaler followed by LDA with solver="lsqr", shrinkage="auto" and equal class priors. No tuning or feature selection is introduced. Central predictions are reused from the original analysis after verifying that the new export is sample-identical. The other three groups require 1,044 new fits. There are 1,392 comparison folds, 288 participant/session configurations and 122,976 held-out predictions. Each configuration predicts every matched trial once.

## Primary no-FORCe results

**100 ms balanced accuracy**, from pooled held-out confusion counts in each session:

| Participant / session | Central | Centroparietal | Posterior | Full |
|---|---:|---:|---:|---:|
| mle01 / pre | 0.676 | 0.665 | 0.651 | 0.667 |
| mle01 / post | 0.695 | 0.496 | 0.530 | 0.738 |
| mle01 / retest | 0.796 | 0.772 | 0.768 | 0.867 |
| spe30 / pre | 0.842 | 0.846 | 0.834 | 0.898 |
| spe30 / post | 0.827 | 0.827 | 0.867 | 0.943 |
| spe30 / retest | 0.654 | 0.662 | 0.644 | 0.731 |

Descriptive mean BA / mean run-AUC across the six participant/session results:

| Channel set | 100 ms | 50 ms | Samples |
|---|---:|---:|---:|
| Central | 0.748 / 0.797 | 0.727 / 0.787 | 0.728 / 0.785 |
| Centroparietal | 0.711 / 0.762 | 0.707 / 0.757 | 0.696 / 0.749 |
| Posterior | 0.716 / 0.764 | 0.708 / 0.758 | 0.704 / 0.758 |
| Full | 0.807 / 0.860 | 0.797 / 0.850 | 0.787 / 0.844 |

## Pilot finding

At 100 ms, Full has the highest descriptive mean balanced accuracy. Full is higher than Central in 5/6 participant/session analyses: 80.7% versus 74.8% on average. The smaller-set waveform audit therefore does not establish that Central is the best decoder channel set. The full 56-feature representation should remain a candidate for subsequent independent evaluation.

## Interpretation and limits

- Group comparisons use identical held-out trials and runs. Differences in feature count are part of the predefined channel-set comparison; no additional feature-count matching or optimisation is attempted.
- Balanced accuracy is the mean of displaced sensitivity and non-displaced specificity. AUC is computed within held-out runs then averaged, because separately fitted models may use different score scales. Both class recalls, confusion counts, run scores and overall accuracy are saved.
- Candidate sets were defined after examining these pilot waveforms. Held-out-run scores help choose a practical baseline within the pilot; confirming that choice requires independent sessions or participants. Selecting the highest score here does not create an unbiased estimate of its future performance.
- The full montage adds FC1 as well as centroparietal and posterior channels. An advantage for Full would not attribute the gain to posterior electrodes alone. Multichannel covariance can add predictive information even when single-channel average-waveform separation is smaller.
- Better classification does not identify a cortical source or establish that the predictive information is specifically a neural ErrP. No population significance claim is made from two participants.
- The decision-tree experiment remains a separate, Central-only comparison. This extension does not add a new tree benchmark.

## Reproduction and outputs

Run the extended `export_central_features.m` once in MATLAB, then run `output/DEC_decoding/DEC_01_pilot_decoders/.venv/Scripts/python.exe output/DEC_decoding/DEC_01_pilot_decoders/analyse_channel_sets.py` from the repository root. The original Central and decision-tree results are preserved.

- `session_metrics.csv`: all 288 results, including class recalls and confusion counts.
- `fold_metrics.csv`: all 1,392 identical-run comparison rows.
- `heldout_predictions.csv`: individual predictions, IDs, scores and channel-set metadata.
- `paired_channel_differences.csv`: same-fold differences from Central.
- `descriptive_pilot_summary.csv`: means by condition, channel set and representation.
- `analysis_settings.json`: exact groups, inherited model settings and trial-selection protocol.
- `primary_channel_comparison.png`: all primary-condition scores.
- `all_conditions_100ms.png`: all processing conditions at 100 ms.
