# AUD_02 — Mouse trajectories and reach outcomes

All **35,210 event-valid reaches** from 25 participants linked to the supplied behavioural table. The no-jump, left-jump and right-jump sequences agreed on every linked trial. The endpoint time and coordinates matched the raw mouse samples on **33,734 reaches**. For the other 1,476, the manuscript values were missing on 1,446 trials and disagreed with the sampled trajectory on 30. [Participant mapping](participant_mapping.csv) · [Coverage](coverage_by_session.csv)

| Selection | Non-displaced | Displaced |
|---|---:|---:|
| Event-valid reaches | 23,426 | 11,784 |
| Verified endpoints | 22,464 | 11,270 |
| EEG-accepted reaches | 20,076 | 10,155 |
| EEG-accepted with verified endpoints | 19,316 | 9,725 |

The EEG-accepted displaced set includes **4,427 correction**, **5,306 error**, **421 slow**, and **one unknown** trial under the manuscript's trajectory criteria. These criteria combine lateral velocity and endpoint distributions. The audit also detects toward-target steering under its proxy rule in **836 displaced trials labelled error** across the event-valid set. [Trial audit](trial_audit.csv.gz)

The report plots the cursor path, target centers, and nominal lateral speed. It shows the verified endpoint distance to the final target center as a continuous measure. The target boundary and a timed outcome cue are unverified, so geometric hit/miss and feedback alignment remain open. The saved endpoint timestamps are offline movement-end estimates verified against the trajectory samples. [Interactive report](../report/index.html#trajectories) · [Methods](../../../Code/analyses/AUD_data_audit/README.md#aud_02)

## Outward follow-through and 250 ms steering

| 250 ms steering status | EEG-accepted displaced trials |
|---|---:|
| Confirmed by 250 ms | 1,620 |
| Confirmed later | 5,963 |
| No detection in the observed outward reach | 1,600 |
| Incomplete outward coverage through 250 ms | 944 |
| Above threshold at the first eligible sample | 28 |

Of the 10,155 EEG-accepted displaced trials, 9,628 had a verified manuscript endpoint within the estimated outward segment. In those same trials, the median manuscript endpoint distance was **345 px**, and the median closest observed distance was **177 px**. On 6,247 trials, the cursor came at least 50 px closer **after** the manuscript endpoint. The 50 px value describes the size of the change in this audit. Distance to center remains a continuous measure.

The last logged sample bounded the outward segment on 6,152 EEG-accepted displaced trials, the return-motion proxy on 3,754, and the nominal target deadline on 249. Closest approach therefore describes the observed outward reach. The fixed window and the distance measures feed the [ERP_02 analysis](../../ERP_event_related_potentials/ERP_02_steering_and_endpoint/RESULTS.md).

## Provisional target boundary

The [target boundary audit](target_boundary/RESULTS.md) provides one observed-hit label per accepted trial using a provisional 40 px circle. Any recorded entry during the eligible segment counts. The same audit saves the detailed radius and endpoint diagnostics.
