# Review of Code/tDCsErrPotential.m

Static review, 9 September 2026. MATLAB script was not executed or modified. Line numbers refer to the inspected file. Helpers removeDC.m and rsquared.m were also read.

## Role and provenance

This is a downstream aggregation, plotting and classification script, not the raw event parser. Lines 54–62 load per-run MAT files and concatenate RunResults.CleanTrials, Trials, Labels, pos and typ without reconstructing events or labels. Thus it inherits the erroneous labels for mle01 trials 76/78; it does not explain the original 255-to-500 omission. A targeted search of available non-BioSig MATLAB/Python files did not locate assignments generating RunResults.typ/pos/Labels.

Currently selects spe30 only (line 18). Linux paths at 4–5 and 27 are not portable to the current workspace. Relative montage loads depend on MATLAB's working directory/path. All subject-directory MAT files are included (39), without an explicit run/training manifest.

## Findings to resolve before reproduction

1. **Incorrect and inconsistent significance calculations (121, 150–153, 196–205, 240–250).** The first threshold is 0.05 / nTime * nChannels, rather than division by both. With 2000 samples and eight channels, this is 0.0002 instead of 0.000003125, a factor of 64. The later threshold fixes the arithmetic but still tests the full four-second epoch. Tests between two scalar grand averages lack within-group variance information. Later code replaces the significance array with a channels-by-time matrix but indexes it as subject-by-channel-by-time; size(...,3) is then 1, so the intended scan over time does not occur. Replace duplicate sections with one trial-level calculation on the documented analysis window.

2. **Downsampling cannot be relied on (441–442).** `1:size(CleanTrials)` supplies a size vector rather than a scalar loop bound; use size(CleanTrials,1). The input slice remains 1-by-time-by-channel, so the operation must explicitly select the time dimension, e.g. operate on a squeezed time-by-channel matrix. Factor 64 would reduce 500 Hz to 7.8125 Hz (Nyquist 3.90625 Hz), incompatible with retaining the paper's 1–20 Hz amplitudes without additional filtering and information loss. The paper reproduction does not require this reduction.

3. **Classifier differs from paper (476–498).** Removes channel 1 while comment says Fz; channel 1 is P3 in the declared montage. Uses four features, leave-one-out CV and quadratic discriminant analysis despite LDA naming. The short paper specifies 100 r-squared-ranked features, 10-fold CV and a decision tree. Ranking is correctly recomputed on training trials within the CV loop; the earlier global ranking is not used to choose that loop's features, so that earlier calculation alone is not classification leakage.

4. **Plot cropping does not crop analysis (216–233, 453–455).** plotRange only changes plotted averages. Statistical tests, rejection and feature extraction still operate on all 2000 samples. Inclusive [-1,+1] plotting selects 1001 points at 500 Hz, whereas the paper describes 1000. Establish one epoch/time convention and explicitly crop the analysis tensor. Topographic timeVector at 401 is shifted one sample relative to 216–217.

5. **Baseline operation differs from its description (88–94).** removeDC subtracts each channel's epoch mean, then line 94 subtracts the resulting first sample. Algebraically the combined operation is x(t)-x(first), so the mean subtraction cancels. In the verified four-second epoch, the first sample is at -2 s, not movement onset at zero. No active bandpass or FORCe call appears here: those stages must have occurred upstream if present. The spectral-filter example is commented out and mentions 1–10 Hz rather than the paper's 1–20 Hz.

6. **Output/provenance handling is incomplete (65–66, 115–116).** The saved CleanTrials file is written before this script's baseline/rejection steps, without aligned labels or a trial manifest. Rejection removes epochs and labels but does not update a run/trial mapping; concatenated Pos remains run-relative. Preserve run identity, original epoch indices and a rejection mask. Rejecting only positive maxima >100 (107) does not detect large negative excursions; decide whether to preserve the paper's literal rule or use absolute amplitude as a documented change. Data-loss quality is not assessed here.

7. **Topographies do not implement the published peak selection (377–409).** Selects extrema over the full epoch using channel 8 (FC1), fixes subject index 1, and also plots arbitrary times 0 and 0.05 s. Match the paper's stated peak times and selection rule for reproduction. Only eight channels are recorded; the commented 64-channel zero-fill example should not be treated as measured data.

8. **Multi-subject execution is incomplete (189 onward).** Later plots/statistics/classification execute after the subject loop and use its last retained CleanTrials/Labels, while topographies explicitly use subject 1. Re-enabling multiple subjects would mix scopes. Keep each subject's processing and outputs together.

9. **Feature helper unnecessarily allocates a square correlation matrix.** rsquared.m replicates labels for every feature, computes feature-by-feature-sized correlations and takes their diagonal. At 16000 features, that intermediate has 256 million doubles (~2 GB before other allocations). Correlating the feature matrix directly against one label column yields the needed vector with much lower memory use.

## Next implementation order

First repair/rebuild upstream event metadata and reconcile epoch labels against mouse logs. Then refactor this script into per-subject loading with a manifest, explicit epoch selection/baseline/rejection, one correct grand-average/significance path, published topographies and paper-matched classification. Preserve original outputs and record differences from the historic implementation. Do not infer the original missing parser has been found in this file.
