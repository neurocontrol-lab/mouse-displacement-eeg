# AUD_01 — Event timing and target-jump audit

The first 3-pixel cursor step matched the logged **movement onset (400)** exactly in **98.6%** of trials. For the **target jump (500)**, the strongest candidate was a forward step cutoff fitted separately within each run. It matched **81.4%** exactly and **87.5%** within ±6 ms. The audit covers all 25 participants. [Cohort results](threshold_comparison.csv) · [Results by participant](threshold_comparison_by_participant.csv)

## Observed marker timing

Marker 300 records initial target appearance, 400 records movement onset, and 500 records the 400-pixel lateral target jump in displaced trials. The intervals below use EEG sample indices at 500 Hz. The mouse and EEG logs agreed on the movement-to-jump interval within 3 ms on all 11,784 displaced trials. [Timing by participant and clock](marker_timing.csv)

| Interval | Trials | Median | Middle 90% | Range |
|---|---:|---:|---:|---:|
| Initial target to movement (300 to 400) | 35,210 | 294 ms | 216–458 ms | 4–998 ms |
| Movement to jump (400 to 500) | 11,784 | 84 ms | 42–166 ms | 18–498 ms |

The Graz paper describes a 50 mm/s movement-onset threshold and a jump within 6 ms of movement onset. A mouse-log sample is about 6 ms, much shorter than the observed 84 ms median interval. The recorded target-coordinate change gives a trial-specific jump time for ERP alignment. The logs measure event timing. Physical screen onset was not measured independently. [Graz protocol](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf) · [ERP_01 alignment](../../../Code/analyses/ERP_event_related_potentials/README.md#erp_01)

## Candidate thresholds

For each candidate, the prediction is the first sample that reaches the cutoff. A **forward step** measures cursor movement toward the target along y between consecutive samples. A **2D step** uses the straight-line distance across x and y. Speed divides the step by the actual sample interval. The nominal conversion of **6 cursor pixels per mm of mouse travel** comes from the paper's setup and gives approximate physical speeds. A 3-pixel step over 6 ms corresponds to about 83 mm/s at that scale. [Graz protocol](https://repository.essex.ac.uk/38379/1/tDCS_ErrP_9th_Graz_BCI_Conference_2024.pdf)

Movement rules search from initial target appearance. Jump rules search from logged movement onset. Both searches are bounded by 1.25 s after the initial target and by the available trial samples. For inferred cutoffs, each run is split into alternating trials. A shared cutoff uses the training trials from all eligible runs. A per-run cutoff uses only the training trials from that run. Both fits maximize exact matches in training and are scored on the other half, then the halves are swapped. All match rates include trials without a predicted crossing. The movement comparison uses 35,210 trials. The jump comparison uses 11,781 because one run has three displaced trials, below the four-trial minimum. [Full workflow](../../../Code/analyses/AUD_data_audit/README.md#aud_01) · [Settings](settings.json)

| Marker | Candidate | Exact | Within ±6 ms | Within one logged sample |
|---|---|---:|---:|---:|
| Movement | Fixed 3 px 2D step | 98.6% | 99.6% | 99.8% |
| Movement | Fixed 3 px forward step | 98.0% | 99.2% | 99.4% |
| Movement | Fixed nominal 50 mm/s forward speed | 21.3% | 45.1% | 48.1% |
| Jump | Fixed 18 px forward step | 41.5% | 47.5% | 48.0% |
| Jump | Fixed 560 mm/s forward speed | 16.9% | 31.7% | 32.9% |
| Jump | Fixed 84 ms from movement onset | 7.3% | 20.0% | 21.2% |
| Jump | Shared forward step | 41.6% | 47.5% | 48.0% |
| Jump | Per-run forward step | 81.4% | 87.5% | 88.1% |
| Jump | Per-run 2D step | 80.0% | 86.7% | 87.5% |
| Jump | Per-run forward speed | 65.8% | 82.1% | 83.2% |
| Jump | Per-run 2D speed | 65.0% | 81.5% | 82.8% |
| Jump | Per-run path length since movement onset | 23.3% | 54.1% | 57.0% |
| Jump | Per-run elapsed time since movement onset | 13.6% | 35.1% | 37.3% |

The median fitted jump cutoff was about **560 mm/s forward** and **583 mm/s in 2D**. The draft uses 50 mm/s for longitudinal movement onset and offset and 150 mm/s for lateral correction. The fixed jump references use the shared step fit, the rounded median fitted forward speed, and the observed median delay. All three were chosen from these recordings, so their scores describe performance on this dataset. The stronger fit for per-run steps supports a rule related to how quickly the cursor moved. Recovering the exact task rule and its parameters would require the original implementation. [All candidate results](threshold_comparison.csv) · [Fitted cutoffs by run and fold](fitted_cutoffs.csv.gz)

The trial-level exports preserve [observed EEG and mouse markers](observed_onsets.csv.gz) and [held-out crossings and signed timing errors](predicted_onsets.csv.gz). Both are compressed CSVs.
