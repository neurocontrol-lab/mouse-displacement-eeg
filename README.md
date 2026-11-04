# EEG responses during ballistic mouse movements

Movement-aligned EEG analysis of displaced versus non-displaced mouse targets in 25 available participants. The presence, morphology and interpretation of an ErrP remain research questions; decoding provides complementary evidence.

## Start here

Use the [experiment registry](EXPERIMENTS.md) to find an analysis, then its category README for the methods and linked scripts.

| Category | Analysis workflow | Local interactive report | GitHub HTMLPreview |
|---|---|---|---|
| **PRE — Preprocessing and artifact handling** | [Methods and steps](Code/analyses/PRE_preprocessing_artifacts/README.md) | [Open](output/PRE_preprocessing_artifacts/report/index.html) | [Preview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/PRE_preprocessing_artifacts/report/index.html) |
| **FEA — Features and repeatability** | [Methods and steps](Code/analyses/FEA_features_repeatability/README.md) | [Open](output/FEA_features_repeatability/report/index.html) | [Preview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/FEA_features_repeatability/report/index.html) |
| **DEC — Decoding and classification** | [Methods and steps](Code/analyses/DEC_decoding/README.md) | [Open](output/DEC_decoding/report/index.html) | [Preview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/DEC_decoding/report/index.html) |

The HTML reports include embedded figures and aggregate data and open directly in a browser. GitHub previews target the `main` branch and become available after the report files are pushed to an accessible repository. Formal PDFs and editable LaTeX are linked from each report.

## Current analysis

Continuous 1–20 Hz no-FORCe preprocessing is the primary reference (PRE_01). PRE_09 evaluates artifact-handling alternatives; FEA_01 audits features and repeatability; DEC_01–03 cover pilot feature/model choices, fixed full-cohort evaluation and Graz-style trees.

The all-eight-channel 100 ms shrinkage LDA achieved 76.3% mean participant balanced accuracy in the 23 non-pilot participants, compared with 70.3% for central LDA. Permutation significance inference remains pending.

## Repository layout

| Location | Contents |
|---|---|
| `Code/analyses/` | Three category READMEs and experiment-specific scripts. |
| `Code/preprocessing/` | Shared event parsing, preprocessing and response-plotting stages; explicit PRE configurations. |
| `Code/helpers/` | Shared analysis functions and the HTML report builder. |
| `Code/experiments.json` | Experiment directory/workflow map used by MATLAB and Python. |
| `Code/FORCe/` | Supplied cleaning library, required binaries and implementation notes. |
| `Code/resources/` | Channel locations used by the analysis. |
| `Code/reference/` | Numerical source reference for the Graz-style feature ranking. |
| `Code/tests/` | Focused parser and FORCe adapter checks. |
| `output/<category>/<experiment>/` | Numerical results, figures and recorded settings. |
| `output/<category>/report/` | Interactive overview, PDF note and LaTeX source. |
| `output/legacy/` | Earlier numerical findings and event audits. |

## Running and reviewing the code

Follow each category README’s workflow tables in order. Shared montage, sample rate and timing conventions are defined in `Code/dataset_config.m`; experiment directory resolution uses `Code/experiments.json`. The shared preprocessing default is the historical PRE_06 FORCe configuration; select a PRE ID explicitly rather than assuming it describes the current no-FORCe analysis.

MATLAB uses Signal Processing Toolbox and, where needed, Statistics and Machine Learning Toolbox. FORCe execution additionally requires Wavelet Toolbox and its supplied Windows x64 binaries. Install Python dependencies using `python -m pip install -r requirements-analysis.txt`. Original recordings must be supplied separately for analyses that read them.

To rebuild HTML summaries from saved results: `python Code/helpers/build_web_reports.py`. This does not rerun preprocessing or fit models. Original recording/trial identities are retained. Historical FORCe reconstructions are preserved because the implementation changed after some runs.

## Research references

- Amaunam et al. (2024), *EEG correlates of error-related activity during ballistic computer mouse movements*, 9th Graz BCI Conference.
- Daly et al., [FORCe: Fully Online and Automated Artifact Removal for Brain-Computer Interfacing](https://doi.org/10.1109/TNSRE.2014.2346621).

[FORCe corrections](Code/FORCe/PATCHES.md) · [FORCe source audit](Code/FORCe/SOURCE_AUDIT.md)
