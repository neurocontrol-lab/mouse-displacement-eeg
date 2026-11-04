# FORCe two-participant results

All available task recordings for **spe30 and mle01** were parsed across pre, post and retest sessions. Of 36 recordings, 29 contained validated trials and were processed with FORCe. There is no one-run-per-session limit. Training and stimulation recordings are outside the task-run analysis.

## Processing scope

Seven spe30 recordings contained no validated trials: the three pre and three post recordings from 17 July 2018, and retest run 2 from 19 July 2018. Their mouse-log trial count, order or timing checks failed. They remain documented in the shared `../PRE_01_no_force_reference/parsed/manifest.csv` and are excluded from cleaning.

The 29 eligible recordings contain 2,915 trial rows. FORCe processing retained 2,613. The full parsed manifest contains 3,624 trial rows, including 709 in the seven excluded recordings.

## Results against PRE_01

Counts use the same recordings and trial identities in both pipelines. Recovered and lost mean accepted only in PRE_02 or only in PRE_01, respectively.

| Participant | Session | Runs | PRE_01 accepted | FORCe accepted | Common | Recovered | Lost |
|---|---|---:|---:|---:|---:|---:|---:|
| spe30 | pre | 5 | 496 | 496 | 496 | 0 | 0 |
| spe30 | post | 5 | 498 | 498 | 498 | 0 | 0 |
| spe30 | retest | 4 | 393 | 394 | 393 | 1 | 0 |
| mle01 | pre | 5 | 475 | 484 | 475 | 9 | 0 |
| mle01 | post | 5 | 335 | 354 | 335 | 19 | 0 |
| mle01 | retest | 5 | 374 | 387 | 373 | 14 | 1 |

Across both participants: **2571 PRE_01 accepted, 2613 FORCe accepted, 43 recovered and 1 lost**. Increased retention alone does not demonstrate better physiological signal preservation.

## Rejection reasons within eligible recordings

| Reason | Trial rows |
|---|---:|
| `data_loss_gap_or_filter_edge` | 75 |
| `mouse_trial_count_order_or_timing` | 30 |
| `force_channel_threshold` | 192 |
| `incomplete_or_duplicate_events` | 4 |
| `amplitude` | 1 |

`force_channel_threshold` means at least one channel exceeded the supplied positive 200-microvolt threshold. The adapter excludes these windows because channel interpolation remains unvalidated; it does not count them as successfully cleaned.

## Method and interpretation

Stage 2 filters valid continuous segments at 1–20 Hz, extracts [-1,1) second epochs, applies the supplied FORCe implementation to two independent one-second halves, baselines [-0.2,0), and rejects amplitudes above 100 microvolts. Final rejected epochs remain NaN. The existing FORCe code includes the fixes described in [PATCHES.md](../../../Code/FORCe/PATCHES.md).

The join between independently cleaned halves falls at movement onset. Earlier inspection found enlarged discontinuities there; processing more recordings does not resolve that methodological issue. Window placement still needs review before interpreting the cleaned ErrP. No new seam diagnostic or correction was introduced for this run.

This is a complete two-participant processing run over eligible task recordings, not a full-cohort analysis. No group inference was performed.

## Outputs

- `../PRE_01_no_force_reference/parsed/manifest.csv`: shared event metadata; filter to spe30 and mle01 for the 36 recordings and their event-validity counts.
- `selected_manifest.csv`: the 29 recordings used for cleaning.
- `processed/`: final epochs, trial metadata and rejection-reason CSVs for each selected recording.
- `figures/by_session/`: six participant/session PNG and MAT results, plus `session_counts.csv`.
- `comparison/`: twelve before/after figures using common trials or each version’s own accepted trials, plus `comparison_counts.csv`.

Stages 1–3 and `compare_experiments` completed. Comparison checks confirmed matching labels and movement sample identities. Existing PRE_01 outputs were preserved: all 1,687 file names, sizes and modification times match the prior inventory.
