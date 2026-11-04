# Confirmation of mle01 trials 76 and 78

Source run: `20181113091555_mle01_retest_run3_EEG`.
Mouse log: `20181113091557_mle01_retest_run3_tdcserror_.csv`.

All 100 saved movement positions (`RunResults.pos` where `typ==400`) exactly equal the 100 raw column-12 movement positions, in order. Raw trial boundaries (code 100) independently identify the two events as trials 76 and 78.

| Trial / saved epoch | 400 sample (one-based) | 500 sample (one-based) | Saved label | Mouse target x change |
|---|---:|---:|---:|---|
| 76 | 178531 | 178564 | 1 (Correct) | 508 to 108 |
| 78 | 183204 | 183238 | 1 (Correct) | 508 to 108 |

For an independent waveform check, raw EEG was converted from nV to microvolts and continuously filtered with a fourth-order Butterworth 1–20 Hz bandpass using scipy.signal.sosfiltfilt at 500 Hz. Four-second candidate epochs were taken from 1000 samples before each movement marker to 999 samples after it. Each saved RunResults.Trials epoch was flattened across samples/channels, mean-centered, and correlated against all 100 candidate epochs.

- Saved epoch 76 matched raw trial 76 best: r=0.9999999913; next best r=0.8081.
- Saved epoch 78 matched raw trial 78 best: r=0.9999999992; next best r=0.4044.
- Stored Trials epochs 77/78 and 78/79 also have exactly equal overlapping waveform samples at the offsets implied by their saved movement positions.

This confirms the raw-to-saved Trials indexing for these two epochs. CleanTrials has the same 100-epoch shape, but the FORCe transformation was not rerun or independently inverted. Subject-level aggregate arrays were not traced in this check.

The raw trigger channel and saved RunResults.trigger each contain all 34 code-500 markers, at the same positions. However, RunResults.typ contains only 32 code-500 entries: the markers for these two trials are absent from the derived event list. Both occur amid code-255 activity. This localizes the inconsistency to the derived event-list/label stage rather than missing raw displacement markers. The precise extraction-code defect remains unverified because its generating implementation has not been located.

Conclusion: entries 76 and 78 in this run's Labels vector should be 2 (displaced/error) under the documented class definition. No MAT files or labels were modified. Preserve an audit trail when applying corrections and propagate them through downstream aggregates rather than assuming aggregate indices are also 76 and 78.
