# FORCe filter-order comparison

## Processing and rationale

The agreed experiment is implemented and complete on all 29 eligible recordings from spe30 and mle01. The previous results are preserved.

- **Reference:** continuous 1–20 Hz Butterworth bandpass -> two-second FORCe -> epoch baseline -> amplitude rejection.
- **New:** continuous 1 Hz Butterworth high-pass -> extract two-second epochs -> FORCe -> per-epoch 20 Hz Butterworth low-pass -> epoch baseline -> amplitude rejection.

Both use `filterOrder=4`, zero-phase `filtfilt`, the same [-1,1) epoch, [-0.2,0) baseline, data-gap guards, 100 microvolt final amplitude limit, and channel-interpolation exclusion policy. Baseline correction remains after cleaning/filtering; no epoch baseline subtraction is performed before FORCe.

The hypothesis is that retaining frequencies above 20 Hz during FORCe gives its artifact criteria access to information removed by the earlier bandpass. The saved comparisons measure the resulting retention and waveforms; they do not directly establish that removed components are artifacts.

## References supporting high-pass before ICA

- [EEGLAB: Filtering](https://eeglab.org/tutorials/05_Preprocess/Filtering.html) recommends high-pass filtering around 1 Hz for ICA and filtering continuous data before epoching.
- [MNE: Repairing artifacts with ICA](https://mne.tools/stable/auto_tutorials/preprocessing/40_artifact_correction_ica.html) recommends high-pass filtering before ICA and baseline correction afterward, noting that ICA cleaning can introduce offsets.
- [MATLAB: filtfilt](https://www.mathworks.com/help/signal/ref/filtfilt.html) explains forward/backward filtering and endpoint-transient handling.

The first two references support general ICA practice, not a validation of this FORCe implementation or proof that the new order is superior for ErrPs. High-pass filtering removes slow drift/DC; epoch baseline correction sets each cleaned trial relative to its pre-movement interval.

## Trial retention

| Participant | Session | Runs | Reference accepted | New accepted | Common | Gained | Lost |
|---|---|---:|---:|---:|---:|---:|---:|
| spe30 | pre | 5 | 496 | 496 | 496 | 0 | 0 |
| spe30 | post | 5 | 498 | 498 | 498 | 0 | 0 |
| spe30 | retest | 4 | 394 | 394 | 394 | 0 | 0 |
| mle01 | pre | 5 | 484 | 484 | 484 | 0 | 0 |
| mle01 | post | 5 | 354 | 357 | 352 | 5 | 2 |
| mle01 | retest | 5 | 385 | 387 | 384 | 3 | 1 |

Across 2,915 trial rows, the reference accepts **2,611** and the new pipeline accepts **2,616**: **2,608 common, eight gained and three lost**. Run selection, trial labels, time axes and channels match. All spe30 session counts are unchanged.

Acceptance changes relative to the reference:

- Six previously channel-threshold-rejected trials are now accepted.
- Two previously accepted trials now exceed the channel threshold.
- Two previously amplitude-rejected trials are now accepted.
- One previously accepted trial is rejected because FORCe removed all independent components.

## Matched-trial waveform results

All measurements below use only trials accepted by both methods. Correlations/RMS differences describe condition averages over 0.2–1 s, for all 96 participant/session/condition/channel combinations.

- Median waveform correlation: **0.992**; range 0.957–0.997.
- Median RMS waveform difference: **1.06 µV**; range 0.53–2.89 µV.
- Median maximum-channel onset step: **0.570 -> 0.417 µV**.
- Median typical nearby step: **0.582 -> 0.424 µV**.

Both onset and nearby steps decrease by roughly 27%. This is a broader smoothing change, unlike the earlier window-length comparison where the reduction was concentrated at the internal join. A smaller onset step here is not independent evidence of better artifact detection. The example mle01 retest comparison shows broadly similar timing/shape with visibly smaller amplitudes in several channels. High correlation does not mean equal amplitude or verified preservation of neural signals.

## Pre-movement differences between conditions

This compares **displaced minus non-displaced condition averages within each pipeline**, using exactly the same trials accepted by both pipelines. It is distinct from the post-onset correlation between pipeline versions. Each condition average is computed across all common trials in that participant/session; channels and time samples receive equal weight.

**Metric:** RMS condition difference = sqrt(mean((mean_displaced(t, channel) - mean_non_displaced(t, channel))^2)), pooled over all eight channels and samples in the stated interval. Values are in microvolts; lower values indicate closer condition averages, not proven artifact removal. N/D are the numbers of common non-displaced/displaced trials.

The full pre-zero interval is [-1, 0) s. The additional [-1, -0.2) s interval excludes the baseline interval. Both use saved, already-baselined epochs; excluding baseline samples does not undo baseline correction. The signed mean condition difference over [-0.2, 0) is constrained to approximately zero by baseline correction, so it would not be a useful cleaning metric.

| Participant | Session | Common N / D | Pre-zero RMS: BP then FORCe | Pre-zero RMS: HP → FORCe → LP | Before-baseline RMS: BP then FORCe | Before-baseline RMS: HP → FORCe → LP |
|---|---|---:|---:|---:|---:|---:|
| spe30 | pre | 326 / 170 | 1.408 | 1.007 | 1.555 | 1.113 |
| spe30 | post | 329 / 169 | 0.864 | 0.497 | 0.945 | 0.517 |
| spe30 | retest | 261 / 133 | 1.383 | 0.778 | 1.529 | 0.851 |
| mle01 | pre | 317 / 167 | 1.150 | 0.682 | 1.255 | 0.669 |
| mle01 | post | 233 / 119 | 0.635 | 0.474 | 0.684 | 0.476 |
| mle01 | retest | 246 / 138 | 1.067 | 0.778 | 1.160 | 0.839 |

The new pipeline has a lower full pre-zero RMS condition difference in **6 of 6** participant/session comparisons, and a lower before-baseline RMS difference in **6 of 6**. These are descriptive comparisons without significance testing. Smaller differences are consistent with increased pre-movement agreement, but can also arise from amplitude attenuation or smoothing. They do not demonstrate selective artifact removal or establish that the conditions should be identical before movement.

Inputs: matching `processed/*_EEG.mat` epochs and `*_quality.csv` acceptance/condition fields from `pipeline_v2_1` and `pipeline_v2_2`, selected by the latter’s `selected_manifest.csv`. Trial identity, labels, movement samples, time axes and channel order were checked for equality. No processing outputs were regenerated.

## Interpretation and limits

The new sequence is available as `cfg.filterPlacement='split'` and is the current experimental setting. Setting it to `'before'` restores the reference pipeline and output location. The small retention gain and similar average shapes are encouraging compatibility results, not grounds for concluding superior physiological artifact removal. No significance test or group inference was performed.

This is a comparison of two practical pipelines, not a perfectly isolated ordering experiment: the reference uses a combined bandpass on continuous data, while the new method separates high-pass and low-pass designs and applies the latter on short cleaned epochs. Separate designs do not have precisely the same response as the combined bandpass, and epoch-edge filtering may contribute to differences. The low-pass uses MATLAB filtfilt endpoint handling with no extra padding or smoothing. These limitations matter especially near the epoch ends.

## Saved outputs

- `processed/`: 29 final epoch MAT files and trial-quality CSVs.
- `figures/by_session/`: six participant/session plots and MAT results.
- `comparison/*_common.png`: averages on identical retained trials.
- `comparison/*_own.png`: averages using each pipeline’s retained trials.
- `comparison/*_onset.png`: closer onset views.
- [Retention and onset summary](comparison/comparison_counts.csv).
- [Per-trial onset and nearby-step measurements](comparison/onset_steps.csv).
- [Condition-average waveform measurements](comparison/waveform_comparison.csv).
- [Example: mle01 retest, common trials](comparison/mle01_retest_common.png).

New results are solid; reference results are dashed. All earlier pipeline output directories remain unchanged.
