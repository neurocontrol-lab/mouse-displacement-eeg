# Experiment registry

Experiments are grouped by their scientific purpose. IDs are permanent within each category; a later number does not imply a preferred processing method.

## Categories

| Prefix | Category | What it covers | Methods and script order | Interactive report |
|---|---|---|---|---|
| **PRE** | Preprocessing and artifact handling | Filtering, FORCe application, input quality, rejection and their effects on event-related waveforms. | [Workflow tables](Code/analyses/PRE_preprocessing_artifacts/README.md) | [Open](output/PRE_preprocessing_artifacts/report/index.html) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/PRE_preprocessing_artifacts/report/index.html) |
| **FEA** | Features and repeatability | Channel/time feature comparisons and consistency of averaged responses within participants. | [Workflow tables](Code/analyses/FEA_features_repeatability/README.md) | [Open](output/FEA_features_repeatability/report/index.html) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/FEA_features_repeatability/report/index.html) |
| **ERP** | Event-related potentials | Waveform alignment, timing and morphology. | [Workflow tables](Code/analyses/ERP_event_related_potentials/README.md) | [Open](output/ERP_event_related_potentials/report/index.html) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/ERP_event_related_potentials/report/index.html) |
| **DEC** | Decoding and classification | D/ND classifiers, held-out-run evaluation and Graz-style feature comparisons. | [Workflow tables](Code/analyses/DEC_decoding/README.md) | [Open](output/DEC_decoding/report/index.html) · [HTMLPreview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/DEC_decoding/report/index.html) |

## PRE: Preprocessing and artifact handling

| Experiment | Question / comparison | Scope | Inputs | Workflow | Results | Status |
|---|---|---|---|---|---|---|
| **PRE_01** No-FORCe reference | Shared event parsing and continuous 1–20 Hz filtering, followed by two-second epochs, baseline and rejection. | 25 available participants | Raw data | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_01) | [Open](output/PRE_preprocessing_artifacts/PRE_01_no_force_reference/) | Reference/cache |
| **PRE_02** One-second FORCe windows | Compare two independently cleaned one-second halves joined at movement onset. | mle01 and spe30; 29 runs | PRE_01 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_02) | [Open](output/PRE_preprocessing_artifacts/PRE_02_force_1s_windows/) | Historical |
| **PRE_03** Two-second FORCe windows | Test whether cleaning the full two-second epoch reduces the onset discontinuity. | Two pilots; 29 runs | PRE_02 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_03) | [Open](output/PRE_preprocessing_artifacts/PRE_03_force_2s_windows/) | Historical |
| **PRE_04** Split filtering | Apply continuous 1 Hz high-pass before two-second FORCe and epoch 20 Hz low-pass afterward. | Two pilots; 29 runs | PRE_03 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_04) | [Open](output/PRE_preprocessing_artifacts/PRE_04_split_filtering/) | Historical |
| **PRE_05** FORCe coding fixes | Compare the then-current coding corrections with the preceding split-filter output. | Two pilots; 29 runs | PRE_04 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_05) | [Open](output/PRE_preprocessing_artifacts/PRE_05_force_coding_fixes/) | Historical; source subsequently partly reverted |
| **PRE_06** Full-cohort FORCe run | Earlier all-participant FORCe visual review. This is separate from the primary no-FORCe decoder analysis. | 25 available participants | PRE_01 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_06) | [Open](output/PRE_preprocessing_artifacts/PRE_06_force_full_cohort/) | Historical |
| **PRE_07** Boundary analysis | Compare four matched filtering/cleaning conditions, boundary changes and signal spreading. | Two pilots; 29 runs | PRE_01 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_07) | [Open](output/PRE_preprocessing_artifacts/PRE_07_boundary_analysis/) | Completed |
| **PRE_08** Input-quality screen | Characterise suspected input contamination in one-second windows before reviewing cleaner outputs. | Two pilots; all eight channels | PRE_01 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_08) | [Open](output/PRE_preprocessing_artifacts/PRE_08_input_quality/) | Completed; expert assessment remains separate |
| **PRE_09** Retention and matched ERP comparison | Map input flags to final decisions, screen accepted outputs and compare identical Correct/Error trial waveforms. | Two pilots; 2,562 trials in the four-condition intersection | PRE_07, PRE_08 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_09) | [Open](output/PRE_preprocessing_artifacts/PRE_09_retention_and_erp/) | Completed |
| **PRE_10** Individual-trial onset diagnostics | Inspect the earlier one-second/two-second onset discontinuities and revised preprocessing evidence. | Two pilots | PRE_02, PRE_03 | [Steps](Code/analyses/PRE_preprocessing_artifacts/README.md#pre_10) | [Open](output/PRE_preprocessing_artifacts/PRE_10_onset_diagnostics/) | Historical saved-output investigation |

## FEA: Features and repeatability

| Experiment | Question / comparison | Scope | Inputs | Workflow | Results | Status |
|---|---|---|---|---|---|---|
| **FEA_01** Feature audit and repeatability | Compare channel sets, time-point amplitudes, 100 ms bins and within-participant waveform repeatability. | Two pilots; 2,562 matched trials | PRE_07, PRE_09 | [Steps](Code/analyses/FEA_features_repeatability/README.md#fea_01) | [Open](output/FEA_features_repeatability/FEA_01_feature_audit/) | Completed |

## ERP: Event-related potentials

| Experiment | Question / comparison | Scope | Inputs | Workflow | Results | Status |
|---|---|---|---|---|---|---|
| **ERP_01** Movement and target-jump alignment | Compare matched D/ND waveform morphology at movement onset and recorded target jumps using fixed-window cohort tests and individual run repeatability. | 25 participants; 23 non-pilots in group tests | PRE_01, DEC_02 | [Steps](Code/analyses/ERP_event_related_potentials/README.md#erp_01) | [Open](output/ERP_event_related_potentials/ERP_01_event_locked_waveforms/) | Completed |

## DEC: Decoding and classification

| Experiment | Question / comparison | Scope | Inputs | Workflow | Results | Status |
|---|---|---|---|---|---|---|
| **DEC_01** Pilot decoders | Compare shrinkage LDA channel sets, 100/50 ms bins and samples across four processing conditions; include the pilot tree comparison. | mle01 and spe30; matched trials | FEA_01, PRE_09 | [Steps](Code/analyses/DEC_decoding/README.md#dec_01) | [Open](output/DEC_decoding/DEC_01_pilot_decoders/) | Completed; exploratory selection |
| **DEC_02** Full-cohort decoders | Evaluate fixed all-eight-channel LDA, central LDA and an all-channel tree on held-out runs within each participant/session. | 25 participants available; 23 non-pilots analysed separately | PRE_01, DEC_01 | [Steps](Code/analyses/DEC_decoding/README.md#dec_02) | [Open](output/DEC_decoding/DEC_02_full_cohort_decoders/) | Completed; inference in DEC_04 |
| **DEC_03** Graz-style feature comparison | Compare a tree with 100 training-selected r-squared amplitudes against predefined binned channel sets. | Same evaluated trials and run folds as DEC_02 | DEC_02 | [Steps](Code/analyses/DEC_decoding/README.md#dec_03) | [Open](output/DEC_decoding/DEC_03_graz_comparison/) | Completed; exploratory feature follow-up |
| **DEC_04** Permutation inference | Within-run label shuffles for full/central LDA, binned tree and Graz-style top-100 tree; participant-specific chance thresholds and corrected p-values. | 23 non-pilots; two exploratory pilots | DEC_02, DEC_03 | [Steps](Code/analyses/DEC_decoding/README.md#dec_04) | [Open](output/DEC_decoding/DEC_04_permutation_inference/) | Completed; 1,999 shuffles |


## Interpretation and next work

PRE_07–09 and FEA_01 use the matched four-condition pilot. DEC_02 includes all eligible no-FORCe trials with complete-context quality checks; DEC_03 reuses those exact evaluated trial IDs and folds.

The PRE interactive report presents eight-channel cohort waveforms by participant/session, with pilot-only all-accepted/matched condition comparisons. DEC_04 completes permutation-based inference for four fixed classifiers; all 23 non-pilot participants pass the primary LDA Holm threshold. ERP_01 compares movement and jump alignment on the same matched pairs and reports fixed-window group tests separately from pilot results. Classification scores alone do not identify an ErrP.

[Initial EEG findings](output/legacy/reports/initial_EEG_findings.pdf) · [Earlier event audit](output/legacy/event_audit/)
