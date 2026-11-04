# Focused retained-trial review

This is a visual screen of selected inputs and saved final outputs, not expert source identification or proof of successful cleaning. The mapping covers the saved boundary pilot: identical three-second segments with one-second FORCe windows and joins at -0.5 and +0.5 s. It does not rerun the older two-second extraction with an onset join.

## What the counts establish

- Every one of the 180 high-pass inputs exceeding 1 mV is rejected in all four conditions. None of those gross examples remains in the final pilot analysis.
- Bandpass no-FORCe and split-filter no-FORCe agree on 2,796/2,799 eligible decisions. The split control retains three additional mle01 trials, all with input flags.
- Comparing bandpass no-FORCe with bandpass FORCe: 2,562 trials are accepted by both, 26 by FORCe only, three by no-FORCe only, and 208 by neither.
- More accepted flagged inputs with FORCe is not evidence of worse cleaning: cleaning can change the waveform enough for an input-flagged trial to pass the final amplitude rule. Conversely, passing that rule does not establish acceptable waveform quality.
- All 41 line-frequency-flagged inputs are rejected in each condition.
- Spe30 has 31 retained higher-frequency-flagged inputs in every condition. Their original 30–90 Hz input feature cannot demonstrate remaining high-frequency contamination after the final 20 Hz low-pass.

## Accepted inputs whose flagged window overlaps the response interval

Overlap means that a flagged one-second window intersects 0.4–0.8 s, not that the abnormal samples themselves were localised there.

| Participant | BP no-FORCe | BP FORCe | Split no-FORCe | Split FORCe |
|---|---:|---:|---:|---:|
| mle01 | 18 | 34 | 20 | 36 |
| spe30 | 53 | 53 | 53 | 53 |

## Selected illustrations

Plots show continuous high-pass input across three seconds in the upper panel. Lower panels show the final baseline-corrected two-second signals for all eight channels. No-FORCe controls use dashed lines; FORCe uses solid lines. Missing lines mean no saved final waveform was available after a precheck failure, not a zero waveform. Acceptance and reasons are printed at the top.

| Review | Trial | Selection | Figure |
|---|---|---|---|
| 1 | mle01 / retest / run 3 / trial 68 | lowFrequencyFlag retained by Split_control | [Open](figures/accepted_review_01.png) |
| 2 | mle01 / post / run 4 / trial 40 | localAbruptFlag retained by BP_control | [Open](figures/accepted_review_02.png) |
| 3 | spe30 / pre / run 5 / trial 58 | lowFrequencyFlag retained by BP_control | [Open](figures/accepted_review_03.png) |
| 4 | spe30 / retest / run 4 / trial 50 | highFrequencyFlag retained by BP_control | [Open](figures/accepted_review_04.png) |
| 5 | mle01 / post / run 5 / trial 9 | retained response-overlap flag; largest final response amplitude | [Open](figures/accepted_review_05.png) |
| 6 | spe30 / post / run 2 / trial 11 | retained response-overlap flag; largest final response amplitude | [Open](figures/accepted_review_06.png) |
| 7 | mle01 / post / run 3 / trial 72 | largest gross input: inspect rejection | [Open](figures/accepted_review_07.png) |

## Initial visual observations

1. **mle01 retest run 3, trial 68:** the split no-FORCe signal passes while bandpass no-FORCe is amplitude-rejected. A broad CP5 deflection remains visible in the retained control; both FORCe conditions stop at the saved channel-threshold precheck. This is a useful inspection candidate, not a confirmed ocular source.
2. **mle01 post run 4, trial 40:** a P3-local broad change remains visible in both no-FORCe outputs, which pass the 100 µV rule. FORCe has no final waveform because its precheck rejects the input. An input abrupt flag can therefore correspond to a broader retained deflection after filtering.
3. **spe30 pre run 5, trial 58:** all conditions pass. A pre-movement deflection and rhythmic activity remain visible; the input slow-feature flag does not establish their source or whether they are unwanted.
4. **spe30 retest run 4, trial 50:** the rapid input fluctuations are visually reduced in the final low-passed traces without requiring FORCe. A slower deflection near +0.6–0.8 s remains, and FORCe changes its amplitude. Neither appearance nor a smaller peak establishes neural preservation or artifact removal.
5. **mle01 post run 5, trial 9:** both no-FORCe outputs pass, although P3 has a broad deflection within the response interval and approaches the amplitude threshold. The full input has a large late change extending into padding; its filtered influence must be considered when reviewing the retained waveform. Split FORCe changes this trace substantially; bandpass FORCe fails its precheck. This is a priority review example.
6. **spe30 post run 2, trial 11:** all conditions pass. A sizeable multichannel response-region deflection remains in the controls, with altered amplitude after FORCe. Without independent source evidence, this could include relevant neural activity and should not automatically be excluded.
7. **mle01 post run 3, trial 72:** the previously identified gross P3 disturbance is rejected by both no-FORCe amplitude rules and by both FORCe prechecks. Its saved rejected control trace is shown only to document the decision.

## Interpretation

The existing no-FORCe quality rules catch the gross pilot disturbances. A small set of retained mle01 broad/local deflections deserves targeted review before the rejection policy is declared sufficient. Input slow and higher-frequency flags are inspection aids; they are not labels of residual contamination. The examples also show why lower final amplitude or greater acceptance alone cannot select a cleaner.

For reproducibility, run `map_saved_decisions.m`, then `summarise_retention.py`, then `plot_retained_examples.m`. These read the saved boundary-pilot results and input screens. Production code and previous reports are unchanged.
