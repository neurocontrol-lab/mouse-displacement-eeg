# EEG responses during ballistic mouse movements

This research project examines EEG activity during a ballistic computer mouse task. On some trials, the target moves while the participant is reaching toward it. We compare EEG aligned to movement onset between **displaced** and **non-displaced** trials to investigate whether the task produces a consistent response to unexpected target movement. The presence, timing, and interpretation of an error-related potential (ErrP) remain open research questions.

The analysis begins at the participant level. A difference between condition averages could reflect a latency shift, overlapping visual or movement-related activity, or an error-related response. We therefore preserve trial identities and session labels, inspect individual waveforms, and treat pooled results and stimulation-related comparisons as later analyses.

## Data and experimental conditions

The repository contains recordings for 25 available participants. EEG and mouse-task logs are organized by participant and by `pre`, `post`, and `retest` sessions. The pipeline selects task runs and excludes training and stimulation recordings. It uses 500 Hz EEG from eight channels: P3, PO3, PO7, CP5, CP1, Cz, FCz, and FC1.

Trial labels are derived by matching EEG event markers with mouse logs. Label 1 denotes a non-displaced target; label 2 denotes a displaced target. Incomplete or conflicting event sequences are retained in the metadata with an invalid-trial reason rather than assigned a condition. The current FORCe baseline has processed all 25 participants: 357 eligible task recordings, with 30,895 retained trials. All 75 sessions and 25 participant overviews are described in the [individual visual review](output/pipeline_v2_3_all/VISUAL_REVIEW.md). The original two-participant pilot is retained separately.

## Analysis

The MATLAB pipeline has four stages:

1. **Parse events:** align EEG markers and mouse logs and save trial-level metadata.
2. **Preprocess epochs:** high-pass the continuous EEG at 1 Hz, extract movement-locked [-1, 1) second epochs, apply FORCe artifact cleaning, low-pass at 20 Hz, baseline over [-0.2, 0) seconds, and reject epochs exceeding 100 µV. Invalid or rejected epoch arrays remain NaN, with their reasons preserved.
3. **Plot participant responses:** generate displaced and non-displaced averages, their difference, and exploratory trial-level significance results for each participant and session.
4. **Estimate group averages:** calculate participant-weighted group summaries when an appropriate set of participants has been processed. This stage was not run for the participant-first visual review.

The default FORCe setting uses two wavelet decomposition levels and cleans each two-second epoch in one window. The supplied MATLAB implementation has documented coding corrections; scientific questions about some thresholds and spectral criteria remain unresolved. Processing choices and pilot comparisons are described in the [pipeline documentation](Code/README_pipeline.md) and [FORCe fix notes](Code/FORCe/PATCHES.md).

The latest pilot (`pipeline_v2_3`) retained 2,617 trials. Its waveforms closely matched the preceding split-filter pilot (`pipeline_v2_2`), which retained 2,616. This comparison checks the effect of coding changes; it does not establish that one version better removes artifacts or that an ErrP has been identified. See the [pilot comparison](output/pipeline_v2_3/CODING_FIX_COMPARISON.md).

## Repository structure

| Location | Contents |
|---|---|
| `data/` | Original EEG recordings and mouse-task logs, grouped by participant. |
| `Code/config.m` | Active participant selection and processing parameters. |
| `Code/stage01_*.m`–`stage04_*.m` | The four analysis stages. |
| `Code/helpers/` | Event parsing, FORCe adapter, and pipeline comparison. |
| `Code/FORCe/` | Supplied FORCe MATLAB library and its compiled histogram helpers. |
| `Code/resources/`, `Code/tests/` | Channel locations and optional checks. |
| `Code/legacy/`, `output/legacy/` | Earlier analysis code and results retained for provenance. |
| `output/pipeline_*/` | Versioned parsed events, processed epochs, figures, and comparison reports. |

## Pipeline versions

All versions retain their own processed outputs. Stage 1 event parsing is shared through `output/pipeline_v1/parsed`, so comparisons use the same trial identities. Versions v2 through v2.3 were evaluated on the two pilot participants across the same 29 eligible runs.

| Version | Output | Processing change | What the pilot showed |
|---|---|---|---|
| **v1** | `output/pipeline_v1/` | Original preprocessing and movement-locked epochs, without FORCe. | Baseline for the [initial FORCe comparison](output/pipeline_v2/VALIDATION.md). |
| **v2** | `output/pipeline_v2/` | Added supplied FORCe cleaning in two adjacent one-second windows per two-second epoch, after the 1–20 Hz bandpass. | Retained 2,613 trials. The window join at movement onset warranted review. |
| **v2.1** | `output/pipeline_v2_1/` | Cleaned each full two-second epoch in one FORCe call; kept filter order and other rules. | Retained 2,611 trials. The [median onset step](output/pipeline_v2_1/WINDOW_COMPARISON.md) fell from 2.794 to 0.571 µV on 2,610 common trials, without a similar change in nearby steps. |
| **v2.2** | `output/pipeline_v2_2/` | Applied continuous 1 Hz high-pass before FORCe and a 20 Hz low-pass afterward, followed by epoch baseline correction. | Retained 2,616 trials. The [comparison](output/pipeline_v2_2/FILTER_ORDER_COMPARISON.md) also reflects differences in filter design and endpoint context, so it does not isolate order alone. |
| **v2.3** | `output/pipeline_v2_3/` | Corrected FORCe IC indexing, FFT-bin labels, and undefined-feature handling; made depth explicit while keeping the default at two levels. | Retained 2,617 trials. The [matched-waveform comparison](output/pipeline_v2_3/CODING_FIX_COMPARISON.md) was close to v2.2; this does not establish better artifact rejection. |

The concise [analysis changelog](CHANGELOG.md) records the methodological changes and links to their detailed reports.

On 2 October 2026, the spike-statistic denominator change and configurable
decomposition depth were reverted; depth is now fixed at two. See the
[reversion notes](Code/FORCe/PATCHES.md). Existing v2.3 outputs describe the
earlier implementation and have not been regenerated with these reversions.

## Reproducing the current participant analysis

The project uses MATLAB with Wavelet Toolbox, Signal Processing Toolbox, and Statistics and Machine Learning Toolbox. The supplied MEX binaries target Windows x64. From the repository root:

```matlab
addpath('Code')
stage02_preprocess_epochs
stage03_plot_errp
addpath('Code/helpers')
plot_participant_overviews
```

Stage 2 reuses the parsed event manifest and runs stage 1 if that manifest is absent. It recomputes the selected runs in the configured output folder. Set `cfg.pilot=true` for the original spe30/mle01 scope. To regenerate the pilot comparison figures after stages 2 and 3:

```matlab
addpath('Code/helpers')
compare_pipeline_versions
```

See [Code/README_pipeline.md](Code/README_pipeline.md) for output fields, checks, and configuration details. The name `stage03_plot_errp.m` reflects the original hypothesis; its plots should be interpreted as movement-locked EEG responses until the source of the condition difference is established.

## Research references

- Amaunam, I., Sultana, M., Rodríguez-Herreros, B., Tadi, T., Leeb, R., & Perdikis, S. (2024). *EEG correlates of error-related activity during ballistic computer mouse movements.* Conference study motivating the present EEG analysis.
- Daly, I., Scherer, R., Billinger, M., & Müller-Putz, G. R. [*FORCe: Fully Online and Automated Artifact Removal for Brain-Computer Interfacing*](https://doi.org/10.1109/TNSRE.2014.2346621). *IEEE Transactions on Neural Systems and Rehabilitation Engineering.* Methodological basis for the artifact-cleaning library.
