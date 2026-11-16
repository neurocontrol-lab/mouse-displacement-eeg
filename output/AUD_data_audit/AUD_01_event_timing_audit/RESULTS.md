# AUD_01 — Event timing and target-jump audit

The first 3-pixel cursor step matched the logged **movement onset (400)** exactly in **98.6%** of trials. For the **target jump (500)**, the strongest candidate was a forward step cutoff fitted separately within each run. It matched **81.4%** exactly and **92.1%** within two logged samples. The audit covers all 25 participants. [Cohort results](threshold_comparison.csv) · [Results by participant](threshold_comparison_by_participant.csv)

## Observed marker timing

Marker 300 records initial target appearance, 400 records movement onset, and 500 records the 400-pixel lateral target jump in displaced trials. The intervals below use EEG sample indices at 500 Hz. The mouse and EEG logs agreed on the movement-to-jump interval within 3 ms on all 11,784 displaced trials. [Timing by participant and clock](marker_timing.csv)

| Interval | Trials | Median | Middle 90% | Range |
|---|---:|---:|---:|---:|
| Initial target to movement (300 to 400) | 35,210 | 294 ms | 216–458 ms | 4–998 ms |
| Movement to jump (400 to 500) | 11,784 | 84 ms | 42–166 ms | 18–498 ms |

The median interval between consecutive mouse log samples in the audited trial windows was **5.98 ms**, equivalent to approximately **167 Hz**.

The Graz paper describes a 50 mm/s movement-onset threshold and a jump timed to movement onset. The observed median interval is 84 ms. The recorded target-coordinate change gives a trial-specific jump time for ERP alignment. The logs measure event timing. Physical screen onset was not measured independently. [Graz protocol](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf) · [ERP_01 alignment](../../../Code/analyses/ERP_event_related_potentials/README.md#erp_01)

## Candidate thresholds

For each candidate, the prediction is the first sample that reaches the cutoff. A **forward step** measures cursor movement toward the target along y between consecutive samples. A **2D step** uses the straight-line distance across x and y. Speed divides the step by the actual sample interval. The nominal conversion of **6 cursor pixels per mm of mouse travel** comes from the paper's setup and gives approximate physical speeds. [Graz protocol](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf)

Movement rules search from initial target appearance. Jump rules search from logged movement onset. Both searches are bounded by 1.25 s after the initial target and by the available trial samples. For inferred cutoffs, each run is split into alternating trials. A shared cutoff uses the training trials from all eligible runs. A per-run cutoff uses only the training trials from that run. Both fits maximize exact matches in training and are scored on the other half, then the halves are swapped. All match rates include trials without a predicted crossing. The movement comparison uses 35,210 trials. The jump comparison uses 11,781 because one run has three displaced trials, below the four-trial minimum. [Full workflow](../../../Code/analyses/AUD_data_audit/README.md#aud_01) · [Settings](settings.json)

| Marker | Candidate | Exact | Within 1 logged sample | Within 2 logged samples |
|---|---|---:|---:|---:|
| Movement | Fixed 3 px 2D step | 98.6% | 99.8% | 99.96% |
| Movement | Fixed 3 px forward step | 98.0% | 99.4% | 99.6% |
| Movement | Fixed nominal 50 mm/s forward speed | 21.3% | 48.1% | 76.7% |
| Jump | Fixed 18 px forward step | 41.5% | 48.0% | 58.9% |
| Jump | Fixed 560 mm/s forward speed | 16.9% | 32.9% | 52.7% |
| Jump | Fixed 84 ms from movement onset | 7.3% | 21.2% | 34.4% |
| Jump | Shared forward step | 41.5% | 48.0% | 58.9% |
| Jump | Per-run forward step | 81.4% | 88.1% | 92.1% |
| Jump | Per-run 2D step | 80.0% | 87.5% | 92.1% |
| Jump | Per-run forward speed | 65.8% | 83.2% | 90.5% |
| Jump | Per-run 2D speed | 65.0% | 82.8% | 90.4% |
| Jump | Per-run path length since movement onset | 23.3% | 57.0% | 75.5% |
| Jump | Per-run elapsed time since movement onset | 13.6% | 37.3% | 56.4% |

The median fitted jump cutoff was about **560 mm/s forward** and **583 mm/s in 2D**. The draft uses 50 mm/s for longitudinal movement onset and offset and 150 mm/s for lateral correction. The fixed jump references use the shared step fit, the rounded median fitted forward speed, and the observed median delay. All three were chosen from these recordings, so their scores describe performance on this dataset. The stronger fit for per-run steps supports a rule related to how quickly the cursor moved. The laptop copy provides a concrete rule to test against the study logs. [All candidate results](threshold_comparison.csv) · [Fitted cutoffs by run and fold](fitted_cutoffs.csv.gz)

The trial-level exports preserve [observed EEG and mouse markers](observed_onsets.csv.gz) and [held-out crossings and signed timing errors](predicted_onsets.csv.gz). Both are compressed CSVs.

## Shared laptop protocol

The laptop code checks the 2D cursor step divided by the game loop's elapsed milliseconds. It uses a strict threshold of **0.5 px/ms** for movement onset and **1.5 px/ms** for the first target jump on a displacement trial. Jump checks begin on the frame after movement onset.

We used the saved cursor coordinates and elapsed log time as a proxy for the original loop timing. Across **25 participants and 357 recordings**, a first crossing of 1.5 px/ms after logged movement onset came **before all 11,784 recorded jumps**. The median lead was **47.9 ms**, with participant medians ranging from 29.9 to 83.8 ms early. There were **0 exact matches**, with 12 within one logged sample and 142 within two. Timestamp differences rounded to integer milliseconds gave 0 exact matches, with 25 within one logged sample and 210 within two.

The study logs store fractional-second timestamps and a trial-number column. The laptop logger writes integer milliseconds and has no trial-number column. The fixed laptop rule fails to reproduce the observed jump times under either replay. The original acquisition loop timing and hospital desktop configuration are needed to identify the deployed threshold. The earlier per-run 2D speed fits, expressed in cursor units, had a median cutoff of **3.44 px/ms** (5th–95th percentiles across runs 2.86–4.51 px/ms, using the median of the two folds per run). This spread describes the fits and may reflect differences in logging, hardware or settings.

The [Graz paper](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf) gives **50 mm/s** for movement onset and describes the jump as timed to that onset. The Rodríguez-Herreros draft describes a **50 mm/s longitudinal movement criterion** applied to smoothed trajectories and a separate **150 mm/s lateral correction criterion**. Neither methods section specifies the laptop's 1.5 px/ms jump threshold. Use the recorded marker 500 and corresponding target-coordinate change for jump alignment.

[Replay results by cohort, participant and recording](laptop_protocol_replay.csv) · [Replay code](../../../Code/analyses/AUD_data_audit/AUD_01_event_timing_audit/check_laptop_protocol.py)
