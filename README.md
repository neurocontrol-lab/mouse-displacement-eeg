# EEG responses during ballistic mouse movements

Movement-aligned EEG analysis of displaced versus non-displaced mouse targets in 25 available participants. The presence, morphology and interpretation of an ErrP remain research questions; decoding provides complementary evidence.

## Start here

- [Experiment registry](EXPERIMENTS.md): questions, dependencies, code and results for every experiment.
- [Original pipeline](Code/original_pipeline/README_pipeline.md): shared event parsing and the earlier processing stages.
- Each experiment has its own README under `Code/analyses/`, with script links and execution order.

## Interactive research reports

The reports are standalone HTML files with embedded figures/data and participant/session controls. They can be opened locally without MATLAB, Python or a web server. HTMLPreview links target GitHub `main`; they become available after these files are committed/pushed and require an accessible repository.

| Analysis | Local report | GitHub HTMLPreview |
|---|---|---|
| Preprocessing and artifact handling | [Open](output/PRE_preprocessing_artifacts/report/index.html) | [Preview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/PRE_preprocessing_artifacts/report/index.html) |
| Features and repeatability | [Open](output/FEA_features_repeatability/report/index.html) | [Preview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/FEA_features_repeatability/report/index.html) |
| Decoding and classification | [Open](output/DEC_decoding/report/index.html) | [Preview](https://htmlpreview.github.io/?https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/DEC_decoding/report/index.html) |

## Current working analysis

No-FORCe continuous 1–20 Hz preprocessing is the primary reference. PRE_09 compares saved artifact-handling alternatives; FEA_01 audits features and repeatability; DEC_01–03 cover pilot selection, full-cohort evaluation and Graz-style trees. The historical original-pipeline default is explicitly PRE_06 (FORCe), and should not be confused with the current primary analysis.

The fixed eight-channel 100 ms shrinkage LDA achieved mean participant-level balanced accuracy 76.3% in the 23 non-pilot participants, versus 70.3% for central LDA. Statistical above-chance inference is pending. See the decoding note for inclusion rules and limitations.

## Repository layout

- `Code/analyses/<category>/<ID_description>/`: analysis scripts and experiment README.
- `Code/helpers/`: genuinely shared event/cleaning helpers.
- `Code/original_pipeline/`: earlier four-stage entry scripts and explicit PRE profiles.
- `Code/experiments.json`: directory map shared by MATLAB/Python path helpers.
- `Code/FORCe/`: supplied library, required binaries, corrections and source audit.
- `output/<category>/<ID_description>/`: saved numerical results and figures.
- `output/<category>/report/`: current HTML, PDF and editable LaTeX research notes.
- `data/`: local original recordings and mouse logs (ignored).
- `tmp/`, `.venv/`: local temporary work and Python environment (ignored).

## Reproduction and review

Install Python dependencies with `python -m pip install -r requirements-analysis.txt` in a local environment. MATLAB uses Signal Processing Toolbox and, for FORCe, Wavelet Toolbox and the supplied Windows x64 binaries. Consult each experiment README for the actual script order and cached input requirements. Raw recordings/caches are not bundled with the shareable reports.

Each run retains original recording/trial identities. PRE_01 holds the single shared parsed-event and baseline-epoch cache. Historical MAT configurations remain unchanged; scripts remap their input paths. Some historical FORCe implementations were later reverted, so saved results are preserved rather than relabelled as outputs of the current library.

## References

- Amaunam et al. (2024), *EEG correlates of error-related activity during ballistic computer mouse movements*, 9th Graz BCI Conference.
- Daly et al., [FORCe: Fully Online and Automated Artifact Removal for Brain-Computer Interfacing](https://doi.org/10.1109/TNSRE.2014.2346621).

[Methodological changelog](CHANGELOG.md) · [FORCe patches](Code/FORCe/PATCHES.md) · [FORCe source audit](Code/FORCe/SOURCE_AUDIT.md)

To rebuild all three HTML overviews from saved results: `python Code/helpers/build_web_reports.py`. This does not rerun preprocessing or refit models.
