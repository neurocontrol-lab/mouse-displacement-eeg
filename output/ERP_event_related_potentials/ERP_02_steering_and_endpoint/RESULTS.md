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

Both distance measures were available on **9,628** accepted D trials with a verified manuscript endpoint in the observed outward segment. In the 200–280 ms Cz/FCz window, the non-pilot median slopes were **−0.07 µV per 100 px** for the manuscript endpoint and **−0.22 µV per 100 px** for closest observed approach. Each participant slope estimates the change in voltage across trials per 100 px farther from the target. A slope farther from zero indicates a larger change per 100 px. A negative slope means higher voltage on closer reaches. The 200–280 ms window had the largest absolute median slope for closest approach. For manuscript endpoint distance, the largest absolute median was +0.18 µV per 100 px in the 280–360 ms Cz/FCz window. In the 200–280 ms window, participant slopes spanned both signs for both distances. The analysis uses continuous distance to the logged target center. Geometric hit/miss and feedback-aligned comparisons remain open pending verification of the target boundary and a timed outcome cue.

[Participant slope plot](distance_associations.png) · [Participant slopes](endpoint_distance_slopes.csv) · [Non-pilot summary](endpoint_distance_summary.csv) · [Trial amplitudes](trial_window_amplitudes.csv.gz) · [Windows](windows.json)
