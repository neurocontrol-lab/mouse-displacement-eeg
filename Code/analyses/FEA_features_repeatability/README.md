# FEA — Features and repeatability

Which channels and temporal representations show useful class differences, and how repeatable are the averaged waveforms within each participant?

[Experiment registry](../../../EXPERIMENTS.md) · [Interactive report](../../../output/FEA_features_repeatability/report/index.html)

## Experiments

| ID | Analysis | Scope | Results |
|---|---|---|---|
| [FEA_01](#fea_01) | Feature audit and repeatability | Two pilots; 2,562 matched trials | [Open](../../../output/FEA_features_repeatability/FEA_01_feature_audit/) |

## Shared conventions

EEG is sampled at 500 Hz across P3, PO3, PO7, CP5, CP1, Cz, FCz and FC1. Raw voltages are converted from nV to µV. Labels 1/2 mean non-displaced/Correct and displaced/Error. Error − Correct is displaced minus non-displaced; these names do not verify an error percept.

Run commands from the repository root. MATLAB analysis uses Signal Processing Toolbox and, where needed, Statistics and Machine Learning Toolbox. Executing FORCe also requires Wavelet Toolbox and the supplied Windows x64 binaries. Install Python dependencies using `python -m pip install -r requirements-analysis.txt`.

The audit uses 2,562 exact recording/trial IDs accepted in all four PRE_07 conditions. Central = Cz/FCz; Centroparietal = CP1/CP5; Posterior = P3/PO3/PO7; Full = all eight. The response feature interval is [0.2,0.9) s. Both 500 Hz time-point amplitudes and 100 ms means are examined.

Repeatability compares averaged waveforms; high shape correlation is not amplitude equivalence or single-trial decoding. Sessions remain separate. Descriptive pilot feature separation does not select the best classifier by itself.

## FEA_01

**Feature audit and repeatability.** Compare channel sets, time-point amplitudes, 100 ms bins and within-participant waveform repeatability.

**Scope:** Two pilots; 2,562 matched trials.

| Step | Script | Operation |
|---|---|---|
| 1 | [extract_matched_features.m](FEA_01_feature_audit/extract_matched_features.m) | Export matched sample-wise and 100 ms feature data. |
| 2 | [analyse_feature_audit.py](FEA_01_feature_audit/analyse_feature_audit.py) | Summarise feature separation and binning effects. |
| 3 | [plot_feature_audit.m](FEA_01_feature_audit/plot_feature_audit.m) | Draw channel/time feature comparisons. |
| 4 | [check_repeatability.m](FEA_01_feature_audit/check_repeatability.m) | Calculate the existing split-half, between-run and between-session checks. |
| 5 | [summarise_repeatability.py](FEA_01_feature_audit/summarise_repeatability.py) | Summarise repeatability. |
| 6 | [plot_repeatability.m](FEA_01_feature_audit/plot_repeatability.m) | Generate the repeatability figures. |

Execute in the table’s order, switching between MATLAB and Python as indicated by the script extension.

```matlab
addpath('Code')
addpath('Code/analyses/FEA_features_repeatability/FEA_01_feature_audit')
extract_matched_features
plot_feature_audit
check_repeatability
plot_repeatability
```

```text
python Code/analyses/FEA_features_repeatability/FEA_01_feature_audit/analyse_feature_audit.py
python Code/analyses/FEA_features_repeatability/FEA_01_feature_audit/summarise_repeatability.py
```


[Saved numerical results and figures](../../../output/FEA_features_repeatability/FEA_01_feature_audit/).

## Research note

The category report folder contains the interactive HTML overview, formal PDF and editable LaTeX. The reviewed LaTeX is the authoritative manuscript source. To rebuild the HTML overviews from saved results: `python Code/helpers/build_web_reports.py`.
