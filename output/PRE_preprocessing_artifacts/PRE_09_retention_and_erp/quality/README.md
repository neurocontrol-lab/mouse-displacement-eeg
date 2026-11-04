# Input flags mapped to final trial decisions

This analysis links existing input-only screens to the saved four-condition boundary pilot. No cleaning is rerun and no new rejection thresholds are applied.

## Conditions

1. BP control: continuous 1–20 Hz, no FORCe.
2. BP FORCe: same bandpass, three separate 1 s FORCe windows.
3. Split control: continuous 1 Hz high-pass, segment-level 20 Hz low-pass, no FORCe.
4. Split FORCe: same split filtering with three 1 s FORCe windows (additional reference).

All use the same 3 s eligible segments, crop to [-1,1) s, a [-0.2,0) baseline and the saved final 100 µV amplitude rule. The cleaning boundaries are -0.5 and +0.5 s.

## Mapping checks

- All 2,799 input-screened trials matched by recording and original trial ID, with identical condition labels and eligibility.
- All 2,915 original trial rows are represented in every condition; 116 were ineligible and do not have input screens.
- Accepted flagged inputs are review candidates, not proven artifacts missed by rejection. A feature can be attenuated by filtering or cleaning, or fall partly in cropped padding.

## Participant summary

| Participant | Condition | Accepted / eligible | Any flag retained / input flagged | >1 mV input retained | Slow retained | HF retained | Local retained | Line retained |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| mle01 | BP_control | 1179 / 1411 | 38 / 268 | 0 | 13 | 0 | 4 | 0 |
| mle01 | BP_FORCe | 1201 / 1411 | 58 / 268 | 0 | 23 | 0 | 3 | 0 |
| mle01 | Split_control | 1182 / 1411 | 41 / 268 | 0 | 15 | 0 | 4 | 0 |
| mle01 | Split_FORCe | 1203 / 1411 | 60 / 268 | 0 | 23 | 0 | 3 | 0 |
| spe30 | BP_control | 1386 / 1388 | 96 / 98 | 0 | 8 | 31 | 0 | 0 |
| spe30 | BP_FORCe | 1387 / 1388 | 97 / 98 | 0 | 8 | 31 | 0 | 0 |
| spe30 | Split_control | 1386 / 1388 | 96 / 98 | 0 | 8 | 31 | 0 | 0 |
| spe30 | Split_FORCe | 1387 / 1388 | 97 / 98 | 0 | 8 | 31 | 0 | 0 |

Flag categories overlap. The >1 mV screen is based on the full high-pass input, not the final bandpassed waveform. HF flags before the final low-pass cannot be interpreted as persistent HF contamination afterwards.

## Outputs

- `trial_flag_decisions.csv`: every trial, condition, decision/reason, input flags and final amplitude/step measurements.
- `retention_by_group_and_flag.csv`: pilot, participant, session and run summaries, each pooled and separated into displaced/non-displaced trials.
- `rejection_reasons.csv`: separate amplitude, FORCe prechecks/failures and unavailable-input reasons.
- `accepted_flagged_trials.csv`: complete list of retained flagged inputs for inspection.
- `flagged_channel_windows.csv`: exact input channel, one-second location, flag and decisions in each condition.
- `paired_decision_counts.csv`: same-trial acceptance agreement and discordance.
- `review_selection.csv` and `figures/`: selected concerning inputs with final outputs for visual review.

The data answer which flagged inputs remain in the accepted set. Expert inspection and output-specific evidence are still needed before calling retained signals contamination.

[Methods, settings and execution order](../../../../Code/analyses/PRE_preprocessing_artifacts/README.md#pre_09)
