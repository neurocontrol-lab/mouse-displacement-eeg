# FORCe applied fixes

The supplied FORCe library has the following local fixes for use in this
analysis. Modified code is marked `Update by Satyam`; original author and
license notices are retained. The previous implementation is retained in Git history.

## Applied fixes

- **Histogram function name (`mi.m`):** the 72-sample branch called the
  missing `hista_72_mex` function. It now calls the supplied `hista__72_mex`
  binary. This corrects an execution error without changing the histogram
  definition.
- **Failure reporting (`FORCe.m`):** an optional second output reports
  rejected channels, rejected independent components, all-component removal,
  and the no-usable-channel abort. This lets the pipeline distinguish failed
  cleaning from valid output, including the original abort path that returns
  the input unchanged. Existing one-output calls remain supported. This diagnostic addition itself does not change cleaning decisions.

## Validation

All 22 specialized MEX lengths matched the supplied MATLAB histogram/MI
reference to 1e-12 on deterministic nonconstant inputs. Cleaned demo-window
samples matched the original FORCe source to 1e-12, and the all-channel abort
reported `no_usable_channels` as expected.

## Pipeline safeguards

The adapter `../helpers/clean_epoch_force.m` calls the supplied library. It
validates dimensions, channel order and finite data, calls FORCe using the
configured one- or two-second windows, and returns cleaned samples with a
success/failure status. Window length is an analysis setting, not a library fix.
Failed windows invalidate the epoch. The pilot also rejects windows requiring
channel interpolation, flat channels and all-component removal. These are
pipeline quality policies, not changes to the FORCe algorithm.

The optional adapter check covers one real epoch and invalid-input handling.

## Coding corrections and refactors

- **IC spike indexing (`FORCe.m`):** use the current IC projection rather than
  repeatedly using IC 1. The source's single-channel denominator is restored
  as described below. This changes the spike vote relative to the source;
  the intended scientific spike formula remains under review.
- **FFT bins (`powerspectrum.m`):** frequency labels now match the selected
  FFT bins. Row and column inputs agree. The legacy doubled FFT magnitudes
  and omitted Nyquist bin are retained; this helper does not compute PSD.
- **Undefined features:** nonfinite IC features, zero spectral normalization,
  unavailable spectral bands and undefined spike statistics fail explicitly.
  The adapter rejects the epoch with `invalid_feature` rather than silently
  treating a NaN comparison as a passed criterion.
- **Decomposition:** depth is fixed at 2, as in the source; cell arrays are
  vectors sized for the channels and terminal nodes. The all-lowpass node is
  identified by its tree index; all other terminals use the detail policy.
- **Unsupported mode and comments:** accelerometer mode fails explicitly;
  window/output comments and the histogram default description are corrected.

## Reversions — 2 October 2026

- **Spike-statistic denominator:** reverted the channel-mean denominator
  introduced in v2.3 to the source's single-channel expression:
  `mean(abs(mean(projIC{iNo}(iNo,spikePos(i)-1:spikePos(i)+1))))`.
  The numerator remains the standard deviation of the absolute channel-mean
  trace. The current-IC indexing correction (`projIC{iNo}`) and finite-feature
  guard remain. This restores the source's denominator construction without
  restoring its repeated-IC-1 indexing bug; it does not resolve the scientific
  formula's interpretation.
- **Configurable decomposition depth:** removed the optional fifth `FORCe`
  argument, the helper's optional depth argument and `cfg.forceLevel`.
  Both library functions use the source's fixed depth of two. The adapter
  again calls the four-input API. Vector cell allocation and explicit
  approximation-node identification remain.

Historical v2.3 and `pipeline_v2_3_all` outputs were not regenerated. Their
saved configurations and comparisons describe the implementation before
these reversions. The denominator reversion can change cleaning decisions;
those historical results must not be presented as validation of this revision.
Static checks confirmed the four-input call and fixed-depth declarations.
MATLAB execution was not performed for this revision.

## Pending scientific clarification

High priority: coefficient sampling rate in spectra; magnitude versus PSD and
threshold units; disabled 1/f vote and added 20 Hz ratio; two-sided kurtosis;
spike-zone formula, neighborhood and paper equation/prose inconsistencies.
These have not been changed by the coding corrections above.

Also unresolved: positive-only 200-microvolt threshold (library and adapter),
coordinate-dependent interpolation (excluded by the adapter), un-restored
SOBI coefficient means, and physical-time lag/neighborhood settings and
available spectral criteria at greater depths. Consult Prof. Perdikis before
altering these scientific choices.

The current pilot keeps two-second windows, two decomposition levels and
HP -> FORCe -> LP processing. Outputs are saved separately in
`output/pipeline_v2_3`, compared with `output/pipeline_v2_2`.

The [completed coding-fix pilot](../../output/pipeline_v2_3/CODING_FIX_COMPARISON.md)
records the focused checks and comparison results.
