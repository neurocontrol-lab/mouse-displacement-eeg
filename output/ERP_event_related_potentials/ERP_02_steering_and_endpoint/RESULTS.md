# ERP_02 — Steering and endpoint distance

This descriptive follow-up uses the primary continuous 1–20 Hz no-FORCe EEG. [ERP_01](../ERP_01_event_locked_waveforms/) remains the all-D versus matched-ND reference. [Methods](../../../Code/analyses/ERP_event_related_potentials/README.md#erp_02) · [Interactive report](../report/index.html)

## Jump alignment

The [trial selection](trial_selection.csv) contains 10,155 accepted displaced trials. Of these, 1,620 had steering confirmed by 250 ms and 7,563 had complete coverage with no confirmation by 250 ms. The other 972 had incomplete coverage or started the search above the threshold. Same-recording, same-side matching yielded **1,154 pairs**, with median absolute differences of 8 ms in reaction time and 6 ms in movement-to-jump delay. The control steered later in 993 pairs and had no detected steering in 161.

At Cz/FCz from 200 to 280 ms after the jump, the early-minus-control mean was **+0.79 µV** across 22 non-pilot participants (1,045 pairs). The median participant difference was +0.28 µV, and 12 of 22 participant differences were positive. At P3/PO3/PO7 from 200 to 400 ms, the mean difference was +0.23 µV and the median was −0.05 µV. The signs varied across participants, and the combined comparison mostly distinguishes earlier from later steering. The averaged Cz and FCz traces show a positive deflection in both matched groups. No eligible pair was available for rle13.

[Eight-channel waveforms](jump_early_steering.png) · [Later and no-detection subsets](jump_control_subsets.png) · [Matched IDs](steering_pairs.csv) · [Participant/session amplitudes](steering_contrast_by_session.csv) · [Non-pilot summary](steering_contrast_summary.csv)

## Steering alignment

All **7,722** accepted D trials with a detected onset supported the full steering-aligned EEG window in the saved movement epochs. The median detected onset in non-pilots was **251 ms** after the jump (5th–95th percentile 190–319 ms), overlapping the 200–280 ms Cz/FCz window. Compare the two alignments on these same trials. The amber bands show the timing of the other event relative to the alignment event, and the dashed amber line shows its median. Both views retain the original movement baseline. In the non-pilot Cz/FCz average, the largest positive sample from 150 to 400 ms after the jump was +4.17 µV at +280 ms. In the steering-aligned view, the largest positive sample from −100 to +150 ms was +3.62 µV at +18 ms. These are descriptive peaks in the average. The jump and steering timings covary, and the waveform can include activity related to both events.

[Jump and steering alignments](jump_and_steering_alignment.png) · [Coverage by session](coverage_by_session.csv)

## Target distance

All three distances were compared on **9,628** accepted D trials with a verified manuscript endpoint in the observed outward segment. The primary distance is the minimum over the full eligible log, including approaches after the estimated outward end. The other panels use the outward-only minimum and manuscript endpoint.

The report also shows the same slope model fitted on **2,358 observed-hit D trials** or **7,270 D trials with no hit detected**, using the provisional 40 px target circle. These filters use the same eligibility rules for all three distance definitions. The corresponding fits include 21 and 23 non-pilot participants, respectively. Full-log distances among hits are bounded by 40 px, so the per-100-px unit expresses the scale of the fitted slope.

Among observed hits, the median full-log slope at Cz/FCz from 280 to 360 ms after the jump was **+4.62 µV per 100 px**. Within a participant, a reach that came **10 px closer to the target center** was associated with **0.46 µV lower mean voltage** in that window. This is a descriptive estimate across the 21 non-pilot participants with a fitted slope. The 10th and 90th percentiles of the participant slopes were −1.08 and +1.25 µV per 10 px farther from the target.

In the 200–280 ms Cz/FCz window, the non-pilot median slopes were **+0.13 µV per 100 px** for the full log, **−0.22** for the outward segment and **−0.07** for the manuscript endpoint. The full-log mean slope was −0.10 µV per 100 px. Signs varied across participants, and the direction of the median depended on the distance definition. The largest absolute full-log median was +0.33 µV per 100 px in the 280–360 ms Cz/FCz window. A negative slope means higher voltage on closer reaches.

[Distance associations in the report](../report/index.html#erp-distance) · [Participant slope plot](distance_associations.png) · [Participant slopes](endpoint_distance_slopes.csv) · [Non-pilot summary](endpoint_distance_summary.csv) · [Trial amplitudes](trial_window_amplitudes.csv.gz) · [Windows](windows.json)
