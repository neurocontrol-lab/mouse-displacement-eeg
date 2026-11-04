# Matched feature audit and repeatability

The report compares Central (Cz/FCz), Centroparietal (CP1/CP5), Posterior (P3/PO3/PO7) and Full sets on 2,562 identical trials across four saved processing conditions. It preserves both original 500 Hz time-point features and seven 100 ms bin means. Pre/post/retest are never pooled in feature or repeatability estimates.

Findings:
- Central features have the largest median absolute standardized class difference in these six pilot sessions at both resolutions; this is not a classifier ranking.
- Bins can conceal opposing components: spe30 pre FCz D-ND spans -14.55 to +17.27 microvolts within 0.5-0.6 s, but the bin mean is -1.56 microvolts.
- The two no-FORCe filtering schemes preserve trial-wise features closely (full-set median r=0.9997).
- Pooled split halves agree more closely than individual run averages. Mle01 post and spe30 retest warrant particular attention for whole-run generalisation.
- Post is not a universal outlier: spe30 pre/post D-ND correlation is 0.911, versus 0.377 pre/retest and 0.159 post/retest (condition 1; channel medians).

Key outputs:
- `trial_bin_features.csv`: complete per-trial, per-condition 56-feature vectors; choose columns by `channel_sets.csv`.
- `timepoint_summary.csv`, `binned_feature_summary.csv`: class means, trial SDs and signed separation at both resolutions.
- `binning_detail_loss.csv`: pointwise ranges and averaging variation within every bin.
- `paired_feature_changes.csv`, `set_processing_summary.csv`: exact same-trial processing comparisons.
- `repeatability_summary.csv`: session-separated split-half, between-run and between-session summaries for both resolutions, every set and all processing conditions.
- `repeatability_half_counts.csv`: equal per-class trial count in each independent half.
- `figures/`: original means/bin means, per-feature maps, repeatability comparisons and cancellation examples.


These are development-pilot diagnostics, not held-out classification, artifact identification or population significance tests. High shape correlation is not amplitude equivalence; pooled halves mix runs and can agree even when individual runs do not. Run comparisons use fewer averaging trials, so reduced run agreement cannot be attributed solely to drift. Channel averaging occurs only in the overview plots; all classifier features retain individual electrodes.


[Current workflow and scripts](../../../Code/analyses/FEA_features_repeatability/README.md#fea_01)

[Methods, settings and execution order](../../../Code/analyses/FEA_features_repeatability/README.md#fea_01)
