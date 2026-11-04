# FORCe trial-level onset check

Fresh comparison after restoring the source spike denominator and fixed two-level API. Both variants use continuous 1 Hz high-pass, the same input sampling rate (500 Hz), supplied fixed two-level decomposition, 20 Hz low-pass after FORCe, the same baseline and rejection policies. One-second cleaning uses two separate calls joined at movement onset; two-second cleaning uses one call. No thresholds were retuned.

Processed all 29 eligible recordings for spe30/mle01 across pre/post/retest. Each method retained 2,617 trials, with 2,616 matched between methods. The matched no-FORCe subset contains 2,573 trials; 43 paired FORCe trials exceed the final 100 microvolt limit without cleaning. The no-FORCe reference is formed from the same high-pass input followed by the same low-pass and baseline.

## Magnitude

Each trial's onset step is the largest absolute channel change from -2 ms to 0 ms. This includes ordinary signal variation; it is not a direct estimate of pure artifact amplitude. Nearby steps provide local context: take the median maximum-channel adjacent-sample change within +/-50 ms, excluding the onset pair.

| Stage and statistic | 1 s windows (microvolts) | 2 s window (microvolts) |
|---|---:|---:|
| Before low-pass: median | 7.974 | 3.503 |
| Before low-pass: 95th percentile | 20.623 | 9.435 |
| Before low-pass: maximum | 40.236 | 20.405 |
| After low-pass: median | 0.539 | 0.423 |
| After low-pass: 95th percentile | 1.397 | 1.049 |
| After low-pass: maximum | 3.330 | 2.469 |
| Nearby before low-pass: median | 3.595 | 3.363 |
| Nearby after low-pass: median | 0.509 | 0.429 |

The median within-trial onset/nearby ratio is 2.177 vs 1.035 before low-pass, and 1.086 vs 1.007 afterward. Two-second onset steps are smaller in 2,182/2,616 trials (83.4%) before low-pass and 1,649/2,616 (63.0%) afterward.

The revised pipeline shows a clear boundary-specific excess before the application filter. Filtering substantially smooths it; the final-signal effect is much smaller and is not a universal improvement in each trial. The earlier 2.794 vs 0.571 microvolt result belongs to the historical bandpass-before-FORCe pilot and must not be used as the current pipeline's final-step magnitude.

## Figures

[Distribution and paired trial scatter](step_distribution.png) includes all 2,616 matched trials. No exclusions were made based on jump size.

Examples are chosen by sorting the one-second pre-low-pass maximum-channel step: nearest median, 75th percentile, 95th percentile, then the three largest values. Every panel uses the same trial and the same channel, chosen as the largest-step channel before low-pass in the one-second method. The two-second value in the plot is for that channel; its all-channel maximum in the CSV can differ.

Dashed blue = one-second cleaning; solid red = two-second cleaning; gray = matched-input no-FORCe reference (final-signal views only). Circles mark the samples at -2 ms and 0 ms. Label 1 means non-displaced; label 2 means displaced. No-FORCe QC 1 passes the 100 microvolt limit; 0 fails and is displayed only as contextual reference.

| Example | Participant/session/run/trial | Channel | Pre-filter step 1 s in selected channel | No-FORCe QC |
|---|---|---|---|---|
| [Median example](example_01.png) | spe30 / retest / 3 / 15 | PO7 | 1 s: 7.973 microvolts | 1 |
| [75th-percentile example](example_02.png) | spe30 / retest / 3 / 99 | CP1 | 1 s: 12.182 microvolts | 1 |
| [95th-percentile example](example_03.png) | spe30 / pre / 1 / 93 | FC1 | 1 s: 20.598 microvolts | 1 |
| [Third-largest](example_04.png) | mle01 / post / 5 / 70 | P3 | 1 s: 35.473 microvolts | 0 |
| [Second-largest](example_05.png) | mle01 / pre / 1 / 58 | PO3 | 1 s: 35.744 microvolts | 0 |
| [Largest](example_06.png) | mle01 / retest / 2 / 28 | PO3 | 1 s: 40.236 microvolts | 1 |

## Interpretation and limits

Single-trial joins can be appreciably larger than condition-average jumps. The current low-pass order changes the practical picture: large pre-filter discontinuities become smooth final traces. Some examples, including the largest pre-filter jump, show substantial broader differences between one- and two-second cleaning. These changes cannot be classified as improved artifact rejection or neural distortion from these traces alone.

This check does not establish classifier impact, preservation of true neural amplitudes/latencies, or the best artifact-removal approach. It does not test the three-second arrangement of centred one-second windows, nor an overlap method. It supports assessing joins and broader waveform changes together. The broader matched-trial removed-signal and condition-difference comparison requested by Mushfika remains a separate next step.

Historical outputs and the main configuration were preserved. New pilot epochs and quality tables are stored in sibling revised_1s and revised_2s directories. Numeric summaries and deterministic example identities are provided alongside these figures.
