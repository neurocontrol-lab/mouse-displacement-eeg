# ERP_04 — Observed target entry and close approach

The Cz/FCz positivity associated with displacement was present when both reaches entered the target circle. Among displaced trials alone, the mean contrast in the same window was smaller and varied with the entry definition and radius.

| Jump-aligned contrast | All matched pairs | Non-pilot pairs | Non-pilots | Mean difference at Cz/FCz, 200–280 ms (µV) |
|---|---:|---:|---:|---:|
| D hit vs D no hit detected | 2,095 | 1,977 | 22 | +0.15 |
| D hit by 400 ms vs D no hit by 400 ms | 1,275 | 1,221 | 22 | +0.45 |
| D within 75 px vs D with no approach within 75 px | 2,481 | 2,250 | 23 | +0.33 |
| D within 100 px vs D with no approach within 100 px | 2,271 | 2,026 | 23 | −0.26 |
| D hit vs ND hit | 2,391 | 2,273 | 22 | +2.76 |

The positive D-minus-ND difference in the 200–280 ms window occurred in 18 of 22 contributing non-pilots. The median was +1.57 µV. This contrast includes the response to the target jump and any associated adjustments in movement. The within-D comparison was positive in 11 of 22 non-pilots for the full observed log. The 400 ms comparison used 6,370 trials with coverage through the cutoff, before matching. Median absolute reaction-time gaps ranged from 10 to 12 ms across within-D comparisons and were 2 ms for D hits versus ND hits. The 95th-percentile gap was 128 ms at 75 px and 145 ms at 100 px. The estimates are descriptive.

## Exploratory cohort window tests

Across the five existing windows, two reached Holm-adjusted p < .05 in the matched-hit contrast. The Cz/FCz difference from 200 to 280 ms was **+2.76 µV** (marginal 95% CI +1.19 to +4.33, Holm p = .0060). The P3/PO3/PO7 difference from 200 to 400 ms was **+1.72 µV** (marginal 95% CI +0.82 to +2.61, Holm p = .0033). Tests use 22 pooled non-pilot participant differences. These windows describe the observed contrast and are used as references for ERP morphology.

[Cohort window tests in the report](../report/index.html#erp-window-tests) · [All five test results](matched_hit_window_tests.csv)

[Interactive report](../report/index.html#savedFigures) · [Group window estimates](group_summary.csv) · [Participant and session estimates](participant_amplitudes.csv) · [Trial coverage](coverage.csv) · [Matched trial IDs](matched_pairs.csv) · [Methods](../../../Code/analyses/ERP_event_related_potentials/README.md#erp_04)

## Matched-hit timing follow-up

The 0–500 ms search used one difference waveform per non-pilot participant (22 participants, 2,273 matched pairs). The two-sided cluster permutation test corrected jointly over time, both electrode groups and both polarities.

| Electrode group | Observed cluster (ms) | Mean D − ND (µV) | Corrected cluster p | Pre / post / retest (µV) |
|---|---|---:|---:|---|
| P3/PO3/PO7 | [220, 360) | +2.24 | .00175 | +1.56 / +2.58 / +1.87 |
| Cz/FCz | [366, 500) | −2.63 | .00720 | −1.18 / −1.97 / −3.49 |
| Cz/FCz | [210, 312) | +2.76 | .01080 | +1.95 / +2.74 / +2.25 |

The late central cluster reached the end of the search interval. Its duration beyond 500 ms is undetermined. The session means use the same pooled intervals and had the same polarity in all three sessions. Pre contributed 19 participants and post and retest contributed 22 each. These are descriptive recurrence checks.

The separate **posterior N100-like window** at P3/PO3/PO7 from 80 to 150 ms was **−1.60 µV** (marginal 95% CI −2.73 to −0.47, nominal p = .0078). This fixed-window result complements the later P3-like positivity.

[Cluster and N100 report](../report/index.html#erp-hit-timing) · [All observed clusters](matched_hit_clusters.csv) · [Session means](matched_hit_cluster_sessions.csv) · [N100 estimate](matched_hit_n100.csv)
