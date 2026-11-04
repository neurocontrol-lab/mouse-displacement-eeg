# Analysis changelog

This records changes to the research pipeline and their observed effects. It is not a dated software patch history. Comparisons below use the same two pilot participants (`spe30`, `mle01`) and all 29 task runs with validated trials unless stated otherwise. Stored outputs remain available by version.

## v2.3 — FORCe coding corrections

- Corrected IC projection indexing in the spike calculation, FFT-bin labels, and handling of undefined features. Made decomposition depth explicit while retaining two levels as the default.
- Retained **2,617 trials**, compared with **2,616** in v2.2; one trial was recovered and none lost. The median common-trial condition-average correlation was **0.99898**.
- See the [comparison](output/PRE_preprocessing_artifacts/PRE_05_force_coding_fixes/CODING_FIX_COMPARISON.md) and [FORCe fix notes](Code/FORCe/PATCHES.md). Scientific questions about spectral criteria, thresholds, and deeper decomposition remain unresolved.

## v2.2 — Filtering around FORCe

- Moved the 20 Hz low-pass to after FORCe while keeping continuous 1 Hz high-pass before epoching and cleaning. Epoch baseline correction remains after cleaning.
- Retained **2,616 trials**, compared with **2,611** in v2.1. The two designs also differ in filter response and endpoint context, so the comparison is not an isolated test of order.
- See the [filter-order comparison](output/PRE_preprocessing_artifacts/PRE_04_split_filtering/FILTER_ORDER_COMPARISON.md).

## v2.1 — Two-second FORCe window

- Replaced two adjacent one-second cleaning calls with one two-second call for each movement-locked epoch. This removed the internal join at movement onset.
- Retained **2,611 trials**, compared with **2,613** in v2. On 2,610 trials accepted by both, the median onset step fell from **2.794 to 0.571 µV** while nearby-step variation stayed similar.
- See the [window-length comparison](output/PRE_preprocessing_artifacts/PRE_03_force_2s_windows/WINDOW_COMPARISON.md). A smoother join does not alone prove improved physiological recovery.

## v2 — Initial FORCe integration

- Added the supplied FORCe MATLAB library through an epoch-cleaning adapter, with trial rejection reasons and preserved metadata.
- Processed 29 eligible runs from two participants and retained **2,613 trials**. This version used one-second FORCe windows and a 1–20 Hz bandpass before cleaning.
- See the [initial pilot results](output/PRE_preprocessing_artifacts/PRE_02_force_1s_windows/VALIDATION.md).

## v1 — Original analysis baseline

- Parsed EEG markers against mouse-task logs and produced the original movement-locked epochs and participant plots without FORCe.
- The validated stage-1 manifest and parsed events in `output/PRE_preprocessing_artifacts/PRE_01_no_force_reference/parsed` are reused by the FORCe versions.
