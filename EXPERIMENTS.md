# Experiment registry

Permanent IDs are category-local: PRE = preprocessing/artifacts; FEA = features/repeatability; DEC = decoding. IDs are not pipeline recommendations. Results and numerical settings are preserved when directories change.

## Current research notes

- **Preprocessing and artifact handling:** [interactive report](output/PRE_preprocessing_artifacts/report/index.html) · [report sources/PDF](output/PRE_preprocessing_artifacts/report/) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/PRE_preprocessing_artifacts/report/index.html)
- **Features and repeatability:** [interactive report](output/FEA_features_repeatability/report/index.html) · [report sources/PDF](output/FEA_features_repeatability/report/) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/FEA_features_repeatability/report/index.html)
- **Decoding and classification:** [interactive report](output/DEC_decoding/report/index.html) · [report sources/PDF](output/DEC_decoding/report/) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/DEC_decoding/report/index.html)

## Experiments

| ID | Question / comparison | Scope | Dependencies | Workflow | Results | Status |
|---|---|---|---|---|---|---|
| **DEC_01** Pilot decoders | Compare shrinkage LDA channel sets, 100/50 ms bins and samples across four processing conditions; include the pilot tree comparison. | mle01 and spe30; matched trials | FEA_01, PRE_09 | [Scripts/README](Code/analyses/DEC_decoding/DEC_01_pilot_decoders/README.md) | [Results](output/DEC_decoding/DEC_01_pilot_decoders/) | Completed; exploratory selection |
| **DEC_02** Full-cohort decoders | Evaluate fixed all-eight-channel LDA, central LDA and an all-channel tree on held-out runs within each participant/session. | 25 participants available; 23 non-pilots analysed separately | PRE_01, DEC_01 | [Scripts/README](Code/analyses/DEC_decoding/DEC_02_full_cohort_decoders/README.md) | [Results](output/DEC_decoding/DEC_02_full_cohort_decoders/) | Completed; permutation inference pending |
| **DEC_03** Graz-style feature comparison | Compare a tree with 100 training-selected r-squared amplitudes against predefined binned channel sets. | Same evaluated trials and run folds as DEC_02 | DEC_02 | [Scripts/README](Code/analyses/DEC_decoding/DEC_03_graz_comparison/README.md) | [Results](output/DEC_decoding/DEC_03_graz_comparison/) | Completed; exploratory feature follow-up |
| **FEA_01** Feature audit and repeatability | Compare channel sets, time-point amplitudes, 100 ms bins and within-participant waveform repeatability. | Two pilots; 2,562 matched trials | PRE_07, PRE_09 | [Scripts/README](Code/analyses/FEA_features_repeatability/FEA_01_feature_audit/README.md) | [Results](output/FEA_features_repeatability/FEA_01_feature_audit/) | Completed |
| **PRE_01** No-FORCe reference | Shared event parsing and continuous 1–20 Hz filtering, followed by two-second epochs, baseline and rejection. | 25 available participants | Raw data | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_01_no_force_reference/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_01_no_force_reference/) | Reference/cache |
| **PRE_02** One-second FORCe windows | Compare two independently cleaned one-second halves joined at movement onset. | mle01 and spe30; 29 runs | PRE_01 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_02_force_1s_windows/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_02_force_1s_windows/) | Historical |
| **PRE_03** Two-second FORCe windows | Test whether cleaning the full two-second epoch reduces the onset discontinuity. | Two pilots; 29 runs | PRE_02 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_03_force_2s_windows/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_03_force_2s_windows/) | Historical |
| **PRE_04** Split filtering | Apply continuous 1 Hz high-pass before two-second FORCe and epoch 20 Hz low-pass afterward. | Two pilots; 29 runs | PRE_03 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_04_split_filtering/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_04_split_filtering/) | Historical |
| **PRE_05** FORCe coding fixes | Compare the then-current coding corrections with the preceding split-filter output. | Two pilots; 29 runs | PRE_04 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_05_force_coding_fixes/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_05_force_coding_fixes/) | Historical; source subsequently partly reverted |
| **PRE_06** Full-cohort FORCe run | Earlier all-participant FORCe visual review. This is separate from the primary no-FORCe decoder analysis. | 25 available participants | PRE_01 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_06_force_full_cohort/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_06_force_full_cohort/) | Historical |
| **PRE_07** Boundary analysis | Compare four matched filtering/cleaning conditions, boundary changes and signal spreading. | Two pilots; 29 runs | PRE_01 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_07_boundary_analysis/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_07_boundary_analysis/) | Completed |
| **PRE_08** Input-quality screen | Characterise suspected input contamination in one-second windows before reviewing cleaner outputs. | Two pilots; all eight channels | PRE_01 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_08_input_quality/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_08_input_quality/) | Completed; expert assessment remains separate |
| **PRE_09** Retention and matched ERP comparison | Map input flags to final decisions, screen accepted outputs and compare identical Correct/Error trial waveforms. | Two pilots; 2,562 trials in the four-condition intersection | PRE_07, PRE_08 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/) | Completed |
| **PRE_10** Individual-trial onset diagnostics | Inspect the earlier one-second/two-second onset discontinuities and revised preprocessing evidence. | Two pilots | PRE_02, PRE_03 | [Scripts/README](Code/analyses/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics/README.md) | [Results](output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics/) | Historical saved-output investigation |

## Historical names

The earlier `pipeline_v1`, `pipeline_v2`, `pipeline_v2_1`, `pipeline_v2_2`, `pipeline_v2_3`, and `pipeline_v2_3_all` runs correspond respectively to PRE_01 through PRE_06. Old names inside immutable MAT/JSON settings and historical PDFs describe their original provenance. The live scripts use experiment paths.

PRE_07/08/09 and FEA_01 use the saved four-condition pilot. DEC_02 uses each no-FORCe accepted trial with additional full-context quality checks; it is not restricted to the pilot four-condition intersection. DEC_03 reuses the exact DEC_02 evaluated trials/folds.

## Pending work

- Participant/session eight-channel waveform presentation for all available participants.
- Permutation-based chance/significance assessment for the fixed all-channel LDA.

These are not marked completed by the directory refactor. Existing scores do not yet carry permutation inference.

## Earlier supporting material

- [Initial EEG findings](output/legacy/reports/initial_EEG_findings.pdf).
- [Early event audit](output/legacy/event_audit/).
- [Original analysis code](Code/legacy/).
