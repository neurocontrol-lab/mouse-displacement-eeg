# FORCe window-length comparison

## Decision

Use a single two-second FORCe call per movement-locked epoch as the working analysis setting (`cfg.forceWindowSeconds = 2`). This avoids an internal concatenation boundary at movement onset. The same supplied library is used without further algorithm changes. The one-second results remain available as the reference.

## Matched analysis

Both methods use the same 29 eligible recordings from spe30 and mle01, across pre/post/retest, with 2,915 trial rows. Seven other recordings contain no validated events and remain excluded. Shared stage-1 metadata, channel order, 500 Hz sampling, 1–20 Hz filtering, gap guards, [-1,1) epoch limits, [-0.2,0) baseline and amplitude rejection are unchanged. The channel-interpolation exclusion policy is also unchanged.

The single change in cleaning is 2 x 500-sample calls versus 1 x 1,000-sample call. Changing window length changes the data used for decomposition and rejection; this is not a numerical-equivalence claim or a post-hoc smoothing/offset correction.

## Onset discontinuity

These measurements use **2,610 trials accepted by both methods**, avoiding differences caused by trial selection. The onset step is the maximum across channels of the absolute sample difference from -2 ms to 0 ms. Nearby-step measurements use the typical maximum-channel adjacent-sample step within +/-50 ms, excluding the onset pair.

| Measurement | 1-second windows | 2-second window |
|---|---:|---:|
| Median onset step (µV) | 2.794 | 0.571 |
| Median nearby step (µV) | 0.586 | 0.582 |
| Median within-trial onset/nearby ratio | 4.560 | 0.984 |
| Largest onset step (µV) | 49.077 | 8.206 |

The median onset step is 79.6% lower. The step decreases in 2,470/2,610 trials (94.6%). Nearby steps remain almost unchanged. This supports removal of a boundary-specific discontinuity rather than uniform attenuation of all local sample changes. These are descriptive comparisons; no significance test or cohort-wide claim is made.

| Participant | Session | Common trials | Median onset step, 1 s (µV) | Median onset step, 2 s (µV) |
|---|---|---:|---:|---:|
| spe30 | pre | 496 | 2.439 | 0.503 |
| spe30 | post | 498 | 2.604 | 0.554 |
| spe30 | retest | 394 | 3.416 | 0.719 |
| mle01 | pre | 484 | 2.511 | 0.617 |
| mle01 | post | 354 | 2.519 | 0.518 |
| mle01 | retest | 384 | 3.320 | 0.562 |

## Retention and waveform changes

The one-second method accepts 2,613 trials; the two-second method accepts 2,611. There are 2,610 common trials, one newly accepted trial and three newly rejected trials. All four changes occur in mle01 retest and are due to the final amplitude threshold.

| Recording | Trial | 1-second result | 2-second result |
|---|---:|---|---|
| mle01 retest run 1 | 3 | amplitude rejection | accepted |
| mle01 retest run 1 | 21 | accepted | amplitude rejection |
| mle01 retest run 1 | 39 | accepted | amplitude rejection |
| mle01 retest run 3 | 84 | accepted | amplitude rejection |

Across 96 participant/session/condition/channel averages, correlations over 0.2–1 s range from 0.962 to 0.998 (median 0.989). RMS waveform differences range from 0.30 to 2.14 µV (median 0.70 µV). These use common-trial condition averages, not single-trial correlations.

The later waveform shapes are broadly similar, but amplitude differences remain. Correlation alone does not establish preservation of true neural activity. The evidence supports using two seconds to avoid the artificial internal join in this offline analysis; it does not establish globally superior artifact removal. No matched runtime benchmark was performed, so a runtime advantage or penalty is not claimed.

## Saved comparisons

- [Counts and condition-level onset steps](comparison/comparison_counts.csv).
- [Individual-trial steps and nearby-step controls](comparison/onset_steps.csv).
- [Later waveform correlations and RMS differences](comparison/waveform_comparison.csv).
- `comparison/*_common.png`: matched-trial averages, all eight channels.
- `comparison/*_own.png`: averages using each method’s retained trials.
- `comparison/*_onset.png`: matched averages around onset.
- [Example onset comparison: spe30 pre](comparison/spe30_pre_onset.png).
- [Example full waveform comparison: mle01 retest](comparison/mle01_retest_common.png).

Two-second results are solid; one-second results are dashed. All 29 processed MAT files and six participant/session plots are saved under this output directory. The original `pipeline_v1` and `pipeline_v2` results were not overwritten.

## Suggested methods wording

Each two-second movement-locked epoch (−1 to +1 s; 1,000 samples at 500 Hz) was cleaned in one FORCe call rather than two independently cleaned one-second halves. This removed the concatenation boundary at movement onset. A paired comparison on the same retained trials showed a lower onset discontinuity with similar nearby sample variation and broadly similar later condition-average waveforms. Other preprocessing and trial-rejection settings were held fixed.
