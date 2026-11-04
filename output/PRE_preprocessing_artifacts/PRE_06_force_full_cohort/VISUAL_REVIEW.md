# Individual participant visual review: FORCe PRE_05

Processed all 25 available participants using the unchanged PRE_05 baseline: continuous 1 Hz high-pass, movement-locked [-1, 1) s epochs, two-level FORCe in one two-second window, 20 Hz low-pass, [-0.2, 0) s baseline correction and 100 microvolt rejection.

All 357 eligible task recordings were processed from 380 recordings in the existing stage-1 manifest. The remaining 23 recordings contain no event-validated trials; see [excluded runs](excluded_runs.csv). No run-count cap was used. Sessions with fewer than five eligible runs reflect event eligibility or available recordings. Historical outputs, including the two-participant PRE_05 pilot, are preserved.

Retained **30,895 / 35,659 trial rows (86.6%)**: **20,546 non-displaced and 10,349 displaced**. This denominator covers selected recordings; it excludes entire recordings without event-validated trials. Saved 75 eight-channel session plots with condition means, differences and exploratory significance marks, and 25 Cz/FCz overviews across sessions.

## Visual findings

All 25 Cz/FCz participant overviews were visually inspected. Selected eight-channel views (ara13 pre, lbo12 post, sto20 post and yle21 pre) were also inspected to check spatial variation. Times below are approximate visual readings, not fitted peak estimates.

- Late differences, often around 0.4–0.9 s after movement, recur in several participants. Examples with a repeated late negative-then-positive difference include bal08, cve01, lbo12 and mle01.
- Timing, polarity and amplitude vary between participants and sessions. den12 and eab31 have weak post differences despite hundreds of retained trials; mka24 and sga12 change response timing across sessions. A universal single peak is not supported by this inspection.
- Shifted condition waveforms often produce alternating positive and negative differences. A difference peak alone does not establish a separate error-related component.
- Cz and FCz are often visually similar. Posterior channels also carry differences: lbo12 post and yle21 pre have broad spatial patterns, whereas sto20 post has a conspicuous posterior difference before movement while the central late response is weak. Channel usefulness must be assessed on single trials.
- Pre-movement condition differences occur in several cases. Check trial/run composition and preprocessing before attributing these to anticipation or neural activity caused by displacement. The current zero-phase filters and whole-epoch FORCe are acausal, so temporal spread from later signal is also possible.
- Very low-count averages must not drive feature selection: rle13 pre retains 8 non-displaced / 2 displaced trials; vco27 pre retains 10 / 2. bro19 post retains 50 / 30. These are retained and flagged, not automatically excluded.

Panels use independent amplitude scales. Compare their numerical axes, not apparent line height. No participant was selected or excluded based on the strength of the plotted condition difference. The overviews omit significance marks; the eight-channel session plots retain the existing exploratory trial-level Bonferroni tests, which do not establish participant generalization.

## Per-participant observations

Counts are retained non-displaced / displaced, in pre, post, retest order. Each link opens a six-panel Cz/FCz overview; corresponding eight-channel plots and numeric averages are in [by_session](figures/by_session).

| Participant | Pre N/D | Post N/D | Retest N/D | Visual observation |
|---|---:|---:|---:|---|
| [ara13](figures/by_participant/ara13_overview.png) | 319/169 | 319/166 | 239/125 | Marked latency differences and alternating difference polarity after movement; response timing changes across sessions. Posterior pre-session response also strong. Some pre-movement condition differences. |
| [bal08](figures/by_participant/bal08_overview.png) | 257/131 | 294/148 | 288/151 | Cz/FCz late negative difference around 0.4–0.65 s then positive around 0.7–0.85 s recurs across three sessions; amplitudes/timing vary. Earlier differences weaker/oscillatory. |
| [bpe06](figures/by_participant/bpe06_overview.png) | 251/130 | 319/167 | 192/100 | Post session shows large positive Cz/FCz difference around 0.2–0.5 s; pre has prominent negative excursion near ~0.25 s then positive late, retest positive ~0.45 s then negative late. Substantial session variability; some pre-movement separation. |
| [bro19](figures/by_participant/bro19_overview.png) | 165/84 | 50/30 | 325/169 | Pre/retest show displaced positive excursion near 0.4–0.5 s and timing-dependent later differences. Post is much less stable/oscillatory with only 80 retained trials (50/30); compare sessions cautiously. |
| [cna07](figures/by_participant/cna07_overview.png) | 187/100 | 173/92 | 295/153 | Large recurring positive displaced-minus-non-displaced difference near 0.4–0.55 s and negative near 0.75–0.85 s, in both Cz/FCz. Cz/FCz traces are very similar; notable pre-movement separation and reduced pre/post retention. |
| [cve01](figures/by_participant/cve01_overview.png) | 336/157 | 323/169 | 309/160 | Late alternating differences recur across sessions: displaced peak around 0.4–0.45 s, non-displaced peak around 0.6 s, then positive difference near 0.75 s. Cz/FCz similar. |
| [den12](figures/by_participant/den12_overview.png) | 300/160 | 283/150 | 300/152 | Pre has a strong positive difference around 0.45–0.5 s; post is weak despite 433 trials; retest shifts earlier with alternating peaks. Timing and shape are not stable. |
| [eab31](figures/by_participant/eab31_overview.png) | 328/163 | 323/168 | 298/151 | Pre has early positive and later negative differences; post conditions largely overlap despite 491 trials; retest positive difference shifts to ~0.35 s. Pre-movement separation also present. |
| [emo24](figures/by_participant/emo24_overview.png) | 198/99 | 283/151 | 122/71 | Small, oscillatory pre difference; post shows a latency shift around 0.2–0.4 s; retest is larger and irregular, with only 193 retained trials and substantial loss/rejection. Cz/FCz very similar. |
| [fbo09](figures/by_participant/fbo09_overview.png) | 328/162 | 317/163 | 246/122 | Pre/retest share a large negative movement-related waveform followed by a late positive peak; condition latency differences produce negative ~0.55–0.65 s then positive ~0.75–0.85 s. Post waveform changes considerably. Cz/FCz similar. |
| [gba12](figures/by_participant/gba12_overview.png) | 318/161 | 322/170 | 303/152 | Late negative difference ~0.45–0.6 s then positive ~0.7–0.85 s recurs, but early positive pre response and substantial pre-movement post/retest differences vary. Cz/FCz differ in amplitudes. |
| [gcr27](figures/by_participant/gcr27_overview.png) | 358/133 | 329/159 | 316/159 | Timing changes strongly: pre difference negative ~0.45 s then positive ~0.75 s; post strongly negative ~0.1–0.35 s; retest negative ~0.6 s then positive ~0.85 s. Post pre-movement separation is large. |
| [lbo12](figures/by_participant/lbo12_overview.png) | 310/159 | 269/143 | 259/134 | Recurring late negative difference ~0.45–0.65 s then positive ~0.75–0.9 s in all sessions and both Cz/FCz. Retest is larger; early differences fluctuate. |
| [ldu23](figures/by_participant/ldu23_overview.png) | 317/121 | 310/143 | 301/143 | Strong oscillatory/latency differences, but their timing changes: pre negative near movement and positive ~0.35/~0.6 s; post positive ~0.4 s; retest positive ~0.3–0.4 s. Pre-movement differences present. |
| [meb17](figures/by_participant/meb17_overview.png) | 142/67 | 307/162 | 243/126 | Pre differences are small with 209 retained trials. Post is dominated by a late peak around 0.7–0.8 s; retest has large earlier and late differences plus a shifted waveform. Not a stable fixed-time response. |
| [mka24](figures/by_participant/mka24_overview.png) | 319/166 | 323/165 | 283/149 | Pre has a positive difference near ~0.35 s; post/retest instead show a negative difference ~0.5–0.6 s and positive ~0.7–0.8 s. Similar Cz/FCz waveforms, with later-session repeatability. |
| [mle01](figures/by_participant/mle01_overview.png) | 317/167 | 238/119 | 250/138 | Recurring late negative difference ~0.45–0.6 s then positive ~0.65–0.8 s across sessions, strongest at retest. Early/pre-movement differences also vary; Cz/FCz very similar. |
| [nfu22](figures/by_participant/nfu22_overview.png) | 324/162 | 318/161 | 319/164 | Large latency-dependent differences across sessions, but post reverses the late order seen in pre/retest. Cz/FCz share the broad shape with different amplitudes. No stable signed fixed-time feature. |
| [nsh23](figures/by_participant/nsh23_overview.png) | 317/167 | 312/167 | 322/169 | Strong differences in every session but peak timing and polarity vary: pre positive ~0.3 s; post negative ~0.2–0.3 s then positive ~0.5 s; retest alternating early and late differences. Pre-movement separation present. |
| [rle13](figures/by_participant/rle13_overview.png) | 8/2 | 261/133 | 328/168 | Pre has only 10 retained trials (8 non-displaced, 2 displaced) and an irregular average; do not interpret peaks. Post/retest have usable counts and late differences, with changing timing. |
| [sga12](figures/by_participant/sga12_overview.png) | 261/140 | 324/162 | 180/94 | Pre/retest show late negative then positive differences; post response shifts to an earlier negative ~0.2 s and positive ~0.4 s. Retest retention is reduced to 274 trials. |
| [spe30](figures/by_participant/spe30_overview.png) | 326/170 | 329/169 | 261/133 | Pre/post have a repeated large late waveform and negative ~0.5 s then positive ~0.65 s difference. Retest differs, with a smaller waveform and differences around ~0.1–0.2/~0.55–0.6 s. |
| [sto20](figures/by_participant/sto20_overview.png) | 323/166 | 325/164 | 295/154 | Pre/post differences are broad and include substantial pre-movement separation; post lacks a strong localized late peak despite 489 trials. Retest shows a clear positive ~0.35 s then negative ~0.55–0.65 s difference. |
| [vco27](figures/by_participant/vco27_overview.png) | 10/2 | 105/60 | 299/156 | Pre has only 12 retained trials (10 non-displaced, 2 displaced) and is unreliable. Post has 165 trials with irregular broad differences. Retest has 455 trials and clearer alternating differences near ~0.25/~0.45/~0.6 s. |
| [yle21](figures/by_participant/yle21_overview.png) | 356/97 | 263/113 | 279/127 | Large response amplitude and latency differences in all sessions, with peaks shifting earlier from pre to post/retest. Alternating late difference recurs but a fixed peak time is not stable; Cz/FCz broadly similar. |

## Retention and timing context

[Participant/session summary](participant_session_summary.csv) lists all 75 sessions, raw and eligible run counts, trial-row denominators and condition counts. [Rejection summary](rejection_summary.csv) preserves the recorded reasons; each trial has one final rejection reason, not an exhaustive list of every possible issue.

| Final reason | Trial rows |
|---|---:|
| ok | 30,895 |
| mouse_trial_count_order_or_timing | 372 |
| incomplete_or_duplicate_events | 75 |
| data_loss_gap_or_filter_edge | 2,674 |
| force_channel_threshold | 1,603 |
| amplitude | 19 |
| force_all_ics_removed | 19 |
| mouse_eeg_event_disagreement | 2 |

Five eligible recordings retained zero trials: 20181114081940_emo24_retest_run3_EEG, 20181113113742_vco27_post_run2_EEG, 20181113114530_vco27_post_run3_EEG, 20181113104433_vco27_pre_run4_EEG, 20181113105307_vco27_pre_run5_EEG. No invalid-feature failure was recorded. An all-ICs-removed rejection remains a rejected epoch, not a successful cleaned signal.

For the 10,349 retained displaced trials, movement-to-displacement marker intervals are 18 / 84 / 498 ms (minimum / median / maximum). These are recorded event intervals, not measured screen latency. The plots remain movement-locked; displacement-locked analysis could clarify timing differences.

## What to compare next

This completes the participant-first descriptive review before feature selection, as proposed in the initial-findings discussion. Keep sessions separate initially; pooling could obscure the observed timing changes.

Compare a small set of broad time-window means or downsampled temporal amplitudes with the simple Cz baseline discussed earlier. Evaluate whether FCz or posterior channels add information and whether latency-sensitive features improve on amplitudes. The observed late interval is a candidate to test, not a finalized feature set.

For within-participant classification, hold out complete runs and separately assess session transfer. For participant generalization, hold out complete participants; select features and fit scaling only within training data. Because these 25 participants have all been inspected, report this as exploratory analysis. Data-informed window/channel choices need selection inside validation folds or an independent test set for an unbiased performance claim.

Include class-balanced performance and the majority-class reference: approximately two-thirds of retained trials are non-displaced. Check whether condition-specific rejection and pre-movement differences affect results. No classifier, feature ranking, group-average analysis or stimulation-effect claim was produced in this step.
