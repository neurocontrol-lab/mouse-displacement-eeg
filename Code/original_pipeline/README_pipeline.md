# Original four-stage workflow

These scripts implement the earlier processing workflow. The recent PRE_07–09, FEA_01 and DEC analyses have separate entry scripts; see the root experiment registry.

## Stages

1. [stage01_parse_events.m](stage01_parse_events.m): align EEG markers and mouse logs. Reuse the PRE_01 parsed manifest when present. Deleting that manifest requests reparsing.
2. [stage02_preprocess_epochs.m](stage02_preprocess_epochs.m): process selected runs according to an explicit PRE profile; preserve trial IDs and rejection reasons. Saved PRE_01 baseline outputs are protected against overwrite.
3. [stage03_plot_errp.m](stage03_plot_errp.m): participant/session means and exploratory trial-level Bonferroni tests. Its significance marks are not classification significance or proof of ErrP identity.
4. [stage04_group_averages.m](stage04_group_averages.m): equal-participant session averages. This is not automatically run for participant-level reviews.

## Explicit configuration

```matlab
addpath('Code', 'Code/original_pipeline')
cfg = config('PRE_02'); % choose deliberately; default is historical PRE_06
stage01_parse_events
stage02_preprocess_epochs
stage03_plot_errp
```

[config.m](config.m) maps PRE_01–06 onto the current directory layout. Shared montage, timing and raw-data conventions live in [dataset_config.m](../dataset_config.m). Historical FORCe code has changed; a current run is not guaranteed to recreate saved PRE_02–06 numerical outputs. Preserve the saved results when reviewing earlier methodological comparisons.

The current primary no-FORCe feature analysis reuses PRE_01 cached epochs. Its additional three-second raw-quality checks are documented in DEC_02; these are not silently supplied by the original stage 2.

## Dependencies and conventions

MATLAB; Signal Processing, Wavelet (FORCe only), and Statistics and Machine Learning toolboxes as required by each stage. EEG is 500 Hz; first eight raw channels are nV and converted to µV. Labels 1/2 denote ND/D. Crop [-1,+1), baseline [-0.2,0), final amplitude rejection 100 µV. Timestamp/loss guards preserve discontinuous-recording exclusions. Exact historical settings remain inside saved MAT files.
