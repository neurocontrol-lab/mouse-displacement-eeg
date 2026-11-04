# FORCe v2.3 coding-fix pilot comparison

The minor update uses the existing pipeline and library, with spe30 and mle01,
all 29 eligible task runs (2,915 trial rows), two-second windows, two decomposition
levels, continuous 1 Hz high-pass -> FORCe -> epoch 20 Hz low-pass, and the same
baseline and final amplitude rule. Stage 1 reuses the pipeline_v1 parsed manifest.
Seven additional raw recordings have no event-valid trials and remain excluded.

Reference: `../pipeline_v2_2`. Current: this directory. Earlier outputs
are preserved. Current curves are solid and reference curves are dashed.

## Applied scope

Correct IC projection/channel indexing in the spike calculation; match FFT labels
to actual bins and accept either vector orientation while retaining legacy
magnitudes; fail explicitly on undefined features; vectorize cell allocation,
identify approximation/detail branches and expose depth with default 2; reject
unsupported accelerometer mode. See [applied fixes](../../../Code/FORCe/PATCHES.md).

The physical coefficient sampling rate, PSD conversion, scientific thresholds,
criterion membership, spike-formula interpretation and other pending questions
have not been changed. This combined coding-fix comparison does not isolate the
contribution of each individual correction.

## Trial retention

2,616 -> 2,617 accepted trials; 2,616 common, one recovered, none lost.

| Participant | Session | Previous | v2.3 |
|---|---|---:|---:|
| mle01 | post | 357 | 357 |
| mle01 | pre | 484 | 484 |
| mle01 | retest | 387 | 388 |
| spe30 | post | 498 | 498 |
| spe30 | pre | 496 | 496 |
| spe30 | retest | 394 | 394 |

Recovered trial: 20181113090152_mle01_retest_run1_EEG, trial 39: amplitude -> ok.

No pilot epochs failed with `invalid_feature`. Final rejection counts: data_loss_gap_or_filter_edge: 75, mouse_trial_count_order_or_timing: 30, force_channel_threshold: 188, incomplete_or_duplicate_events: 4, force_all_ics_removed: 1.

## Common-trial waveforms

Across 96 participant/session/condition/channel averages over 0.2–1 s:

- Correlation: median 0.998979, range 0.992085–0.999872.
- RMS difference: median 0.1872 µV, range 0.0945–0.4425 µV.
- Median onset step: 0.4174 -> 0.4056 µV.
- Median nearby step: 0.4243 -> 0.4151 µV.

The waveforms remain close to the reference. These checks support a minor coding
update, not a claim of superior artifact rejection, unchanged peak latency, or
better generalization. Physiological interpretation still requires review.

## Checks and outputs

Event-parser regression, real-epoch cleaning and invalid-input checks passed.
Spectrum row/column agreement, exact FFT bin positions and preservation of legacy
magnitudes passed. The two-level decomposition coefficients and mixing matrices
matched the previous implementation to 1e-12 on deterministic input. Unsupported
accelerometer mode and an undefined zero-signal spectral feature failed explicitly
as intended. The full MATLAB pilot exited successfully.

Six session plots and 18 comparison plots were generated, with
[retention counts](comparison/comparison_counts.csv),
[waveform measures](comparison/waveform_comparison.csv), and
[onset measures](comparison/onset_steps.csv).
