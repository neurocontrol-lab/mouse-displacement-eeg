# Matched eight-channel ErrP pilot comparison

## Scope

This completes the requested saved-output comparison before preparation of a research note. It does not rerun preprocessing/FORCe, change rejection rules, or create a new manuscript.

The comparison uses the 29 saved boundary-pilot recordings and the same 2,562 trials accepted in all four conditions. Trial identity is recording plus original trial number; `matched_trial_ids.csv` contains the exact IDs. Each participant/session is pooled across its selected runs with equal weight per trial.

Correct denotes non-displaced (label 1); Error denotes displaced (label 2). These are experimental condition labels, not independent confirmation that every displaced event elicited an error percept. Error-Correct is displaced minus non-displaced.

All outputs use movement marker 400 at t=0, the same [-0.2,0) s baseline and [-1,+1) s crop. FORCe processed three separate 1 s windows in a 3 s segment, with joins at -0.5 and +0.5 s. Filtering is held constant within each FORCe/control pair:

1. BP no-FORCe and BP FORCe: continuous 1–20 Hz bandpass before optional cleaning.
2. Split no-FORCe and Split FORCe: continuous 1 Hz HP, optional cleaning, 20 Hz LP over the 3 s segment, then cropping.

Comparing across the two filtering families evaluates the practical implementations; it does not isolate filtering order alone. The main plots use the intersection across all four, avoiding trial-selection confounding at the expense of omitting trials accepted by only some methods.

## Matched trial counts and figures

| Participant | Session | Correct / ND | Error / D | Eight-channel plot |
|---|---|---:|---:|---|
| mle01 | pre | 309 | 166 | [Open](figures/mle01_pre_matched_erp.png) |
| mle01 | post | 218 | 114 | [Open](figures/mle01_post_matched_erp.png) |
| mle01 | retest | 237 | 132 | [Open](figures/mle01_retest_matched_erp.png) |
| spe30 | pre | 326 | 169 | [Open](figures/spe30_pre_matched_erp.png) |
| spe30 | post | 329 | 169 | [Open](figures/spe30_post_matched_erp.png) |
| spe30 | retest | 260 | 133 | [Open](figures/spe30_retest_matched_erp.png) |

Each figure has eight channel rows and three columns: Correct, Error, and Error-Correct. All four outputs appear on the same axes. No-FORCe is dashed, FORCe solid; black/red denote bandpass and green/blue denote split filtering. Cleaning joins are grey dotted lines; onset is black. Correct and Error share the vertical scale within each channel; the difference column has its own scale. Positive voltage is upward.

## Response measurements

`response_metrics.csv` contains signed mean amplitude, RMS, positive/negative extrema and their times, and the signed largest-absolute extremum and its time, for every channel/condition/waveform. The main interval is [0.4,0.8) s; [0.2,0.9) s reproduces the previous broader analysis.

`paired_erp_metrics.csv` contains same-window changes with the filtering-matched controls, the filter-only contrast and the two FORCe implementations. `central_channel_changes.csv` extracts Cz/FCz Error-Correct results in the main interval.

The following table summarises all eight channels and six participant/session averages (48 comparisons per row). Values are descriptive, not population-level significance tests or independent participant replicates.

| Contrast (first minus second) | Median absolute mean-amplitude change (µV) | Maximum absolute mean-amplitude change (µV) | Median waveform-change RMS (µV) | Median absolute negative-extremum time change (ms) |
|---|---:|---:|---:|---:|
| BP FORCe minus BP no-FORCe | 0.808 | 3.590 | 2.042 | 7 |
| Split FORCe minus Split no-FORCe | 0.792 | 4.252 | 2.811 | 10 |
| Split no-FORCe minus BP no-FORCe | 0.104 | 0.238 | 0.108 | 0 |
| Split FORCe minus BP FORCe | 0.226 | 0.510 | 0.836 | 6 |

Peak times are descriptive extrema within a search interval, not validated ERP-component latencies. A shifted extremum can reflect a change in which peak is largest, altered polarity, interval-edge selection, or a cleaning boundary; it need not represent a physiological delay. Smaller amplitudes or smoother traces alone cannot establish artifact removal or signal preservation.


## Interpretation of this matched pilot

- The two no-FORCe controls are close in the main response interval: across 48 channel/session Error-Correct comparisons, median absolute mean-amplitude change is 0.104 microvolts and median waveform-change RMS is 0.108 microvolts.
- Adding FORCe is not numerically neutral: median absolute mean-amplitude change is 0.808 microvolts for bandpass FORCe and 0.792 microvolts for split FORCe. Corresponding waveform-change RMS medians are 2.042 and 2.811 microvolts.
- Split FORCe has fewer output quality-screen flags in the separate residual review, but its Error-Correct waveform changes are not smaller than bandpass FORCe in this matched summary. Fewer outliers or smoother joins therefore cannot establish better response preservation.
- At FCz in spe30 pre, mean Error-Correct over 0.4–0.8 s changes from +1.859 to -1.654 microvolts with bandpass FORCe, and from +2.006 to -2.164 microvolts with split FORCe. This is a change in the sign of the window mean, not evidence that a validated ERP component reverses polarity.
- Some peak-time differences reflect selection of different extrema. No population-level significance, physiological delay, or cleaner superiority is inferred from these two participants.

### FCz Error-Correct mean amplitude, 0.4–0.8 s

| Participant | Session | BP no-FORCe (microvolts) | BP FORCe | Split no-FORCe | Split FORCe |
|---|---|---:|---:|---:|---:|
| mle01 | pre | -0.660 | -0.451 | -0.517 | -0.454 |
| mle01 | post | -1.206 | -0.165 | -0.999 | +0.153 |
| mle01 | retest | -1.965 | -0.260 | -1.812 | -0.633 |
| spe30 | pre | +1.859 | -1.654 | +2.006 | -2.164 |
| spe30 | post | +0.898 | -1.195 | +1.039 | -1.622 |
| spe30 | retest | -1.040 | -1.417 | -0.914 | -1.253 |

The completed checks support retaining no-FORCe as the primary working analysis with targeted review of concerning retained trials, and preserving FORCe as a sensitivity analysis. They do not establish that every no-FORCe trial is clean or that all FORCe-related changes are harmful. The pilot is now ready for synthesis with the input and residual-quality analyses; no further FORCe-specific optimisation is required for this comparison.

## Checks

- All included samples are finite, meet saved acceptance, and have a zero mean over the baseline within numerical tolerance.
- All four conditions use exactly the same trial IDs and labels.
- Broader-window Cz/FCz metrics reproduce the previous saved ERP table to 1e-10 tolerance.
- The separate retention/quality review remains the source for method-specific retained-trial counts and residual concerns.

Reproduce by running `compare_matched_erp.m` in MATLAB, then `summarise_matched_erp.py`. The main numerical outputs and figures remain separate from the earlier notes.

[Methods, settings and execution order](../../../../Code/analyses/PRE_preprocessing_artifacts/README.md#pre_09)
