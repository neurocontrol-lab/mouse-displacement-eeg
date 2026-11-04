# Initial validation

## Full cohort run (10 September 2026)

Completed all 380 recordings from 25 subjects. Event audit: 35,210 validated trial sequences; 23 runs with no validated trials. After unchanged quality rules: 30,353 accepted epochs. Generated 75 subject/session PNG/MAT pairs and three group PNG/MAT pairs. All 25 subjects meet the existing minimum of two trials per condition in each session. Pre: 6520 non-displaced + 3171 displaced; post: 7009 + 3591; retest: 6632 + 3430.

Group outputs are in figures/group_sessions, with contributor tables. Numerically verified all saved group C arrays are 1000 x 8 x 25, correct equals mean(C,3), and difference equals mean(E-C,3), with finite waveforms. The known parser regression test passed. Group tests are paired across subject means and corrected within each session. Two pre-session contributors have only 10 and 11 accepted trials (rle13 and vco27), so equal weighting should be interpreted alongside contributor counts. The earlier two-subject counts below describe prior validation, not the current full cohort.

Executed with MATLAB R2025a. The event-parser regression test passes on the known mle01 retest run: 34 displacement markers retained; trials 76 and 78 labelled 2; duplicated 500 samples collapsed; a missing marker flagged rather than classified as correct.

All 36 run-named EEG recordings are represented in the manifest. Same-day mouse log matching is required. Six early spe30 runs lack matching same-day mouse CSVs; another spe30 run fails strict trial-start alignment. These runs remain in the audit but do not contribute epochs. This is conservative exclusion, not a claim that their EEG cannot be recovered.

Initial accepted counts: spe30 1387; mle01 1184. These differ from the paper because this pipeline uses explicit log validation, a different baseline, absolute-amplitude rejection and conservative loss/edge exclusion. No FORCe cleaning is applied. Do not describe these figures as an exact reproduction.

Session separation was subsequently implemented and the pipeline rerun. Accepted totals are unchanged. Counts (non-displaced / displaced): spe30 pre 326/170, post 329/169, retest 260/133; mle01 pre 309/166, post 220/115, retest 241/133. Current figures are in figures/by_session. Older pooled figures are historical. Bonferroni correction applies within each subject/session's 8000 comparisons, not across the six analyses. This change does not alter the approved baseline or quality rules.

Trials 76 and 78 have corrected condition labels in the new metadata, but are rejected from averaging because their windows overlap data loss/filter-edge exclusion. Legacy per-run and aggregate Labels files remain untouched.

Each processed epoch has 1000 samples at 500 Hz, time -1.000 to +0.998 seconds. Invalid/rejected trials retain their metadata rows and NaN epoch slots. Accepted trials alone contribute to plots. Plot colours: blue non-displaced, red displaced, black difference, gold Bonferroni-significant difference.
