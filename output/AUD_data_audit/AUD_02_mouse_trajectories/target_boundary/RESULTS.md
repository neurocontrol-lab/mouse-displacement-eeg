# AUD_02 — Observed target hits

A hit is detected when the cursor center is inside or on the provisional **40 px** circle around the logged final target at any eligible sample. The search starts at the jump for displaced trials and movement onset for non-displaced trials. It continues while the same target is logged, up to the nominal deadline, log cutoff or first gap over 20 ms. An entry during the outward movement or after an overshoot counts once.

| Trial condition | Hit detected | No hit detected |
|---|---:|---:|
| Displaced (D) | 2,391 | 7,764 |
| Non-displaced (ND) | 15,493 | 4,583 |

The trial file also stores the **minimum distance over the full eligible log** and flags for close approach.

| Provisional approach threshold | Displaced within threshold | Non-displaced within threshold |
|---|---:|---:|
| 75 px | 4,551 | 18,868 |
| 100 px | 5,729 | 19,467 |

At 75 px, 5,964 of 6,499 pre-session ND trials were within the threshold (91.8%). The 100 px threshold is used as a sensitivity check.

The labels describe what was observed in the mouse log. A trial may have no detected hit because the log ended before a later entry. The trial file includes the reason and time at which observation ended. The radius remains provisional.

[Two-class trial labels](observed_hit_trials.csv.gz) · [Boundary sensitivity counts](boundary_counts.csv) · [Detailed trajectory diagnostics](boundary_trials.csv.gz) · [Methods](../../../../Code/analyses/AUD_data_audit/README.md#aud_02)
