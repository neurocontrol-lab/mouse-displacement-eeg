# Event code reference

Updated 9 September 2026. Working subject mapping: S1 = spe30; S2 = mle01.

## Recording layout

Raw `.easy` files: columns 1–8 EEG (nV), 9–11 accelerometer, 12 trigger codes, 13 timestamp (milliseconds). EEG sampling rate: 500 Hz. MATLAB uses `data(:,12)`; Python uses column index 11. Trigger entries index continuous EEG samples, not epochs. Mouse CSVs contain a separate `event` column and explicit trial numbers.

| Code | Meaning | Evidence / certainty |
|---|---|---|
| 0 | No event marker at that EEG sample | Not missing EEG and not a trial label. |
| 100 | New trial / start of return-to-start or preparation phase | Mouse CSV trial number increments at this event. It does not mean correct, successful target acquisition, or movement onset. |
| 200 | Preparation/fixation cue; likely fixation-cross onset | Inferred from event order, mouse position and paper protocol. Exact visual action is not yet verified against the stimulus source. Do not treat as a confirmed display-onset timestamp. |
| 255 | Data-loss flag | Neuroelectrics NIC manual identifies 255 as samples where data loss occurred. In the affected retest run, 1338 such entries match the `.info` lost-packet count. Preserve for quality assessment. |
| 300 | Initial target-onset marker | At the first inspected mouse trial, target coordinates change from (0,0) to (508,700) at this code. Consistent with protocol and extraction script. Physical screen onset was not measured independently. |
| 400 | Movement-onset marker | `data/spe30/trialextraction.m` explicitly starts movement epochs here; mouse trajectories support the interpretation. Exact detection algorithm/threshold implementation remains unverified. |
| 500 | Target-displacement marker | Mouse target x changes by ±400 pixels at this marker; original extraction script uses it to identify displaced/error trials. It does not indicate that the participant failed to hit the target. |

Normal task sequences, ignoring quality flags: `100 200 300 400` for non-displaced and `100 200 300 400 500` for displaced. A marker 100 starts a new trial rather than directly labelling the previous one. Use explicit trial boundaries and validate completeness; absence of 500 alone does not establish a valid correct trial if recording/event completeness is uncertain.

Label conventions differ: the small trialextraction.m script uses 0=correct, 1=error; saved per-run RunResults.Labels uses 1=correct, 2=error. Event codes and class labels are different quantities.

## Confirmed parser discrepancy

Run `20181113091555_mle01_retest_run3_EEG.mat`:

| Trial / saved epoch | Current label | Required condition label | Movement sample | Displacement sample |
|---|---:|---:|---:|---:|
| 76 | 1 | 2 | 178531 | 178564 |
| 78 | 1 | 2 | 183204 | 183238 |

Sample indices are MATLAB one-based. Both displacement markers exist in the raw EEG, saved trigger vector and corresponding mouse log. They are absent from derived typ/pos. After removing codes 100 and 200, selecting only zero-to-nonzero transitions reproduces all 398 saved typ/pos entries exactly. Thus a 255-to-500 transition is missed. This reconstructs the parser behaviour; the original generating implementation has not been located.

Fix event parsing to recognize task-code transitions even when preceded by a different nonzero code. Keep quality flags separately. Decide repeated-marker handling from observed encoding and mouse-log validation rather than counting every repeated sample as a new event. Do not delete EEG samples carrying 255: doing so would change sample indices and timing.

## Timing caveat

Codes 300/400/500 are identifiers, not milliseconds. Recorded movement-to-displacement intervals are often substantially longer than the paper's stated ≤6 ms. Do not equate 400 and 500. Retain both times; use 400 alignment for the paper reproduction. Marker timestamps are not independent measurements of screen refresh or physical movement onset.

## Sources

- `data/spe30/trialextraction.m`.
- `data/mle01/20181113091557_mle01_retest_run3_tdcserror_.csv` and corresponding raw `.easy` / `.info` files.
- First-target example: `data/mle01/20181112091844_mle01_pre_run1_tdcserror_.csv`.
- Short paper `GBCIC2024_paper_97.pdf`: protocol semantics, not a numeric event dictionary.
- Neuroelectrics NIC manual, section VII, NIC file formats: https://www.neuroelectrics.com/api/downloads/NE_P3_UM004_EN_NIC2.1.0_1.pdf

No meeting-audio claim is used here. Codes outside this table have not been defined for this dataset in this audit.
