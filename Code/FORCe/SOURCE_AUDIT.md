# FORCe source fidelity review

Reviewed 2 October 2026. Scope: pause downstream feature/classifier work and
assess how to retain the supplied implementation while using two-second EEG
epochs. No production source, configuration or saved analysis was changed.
The current `PRE_06` includes the two pilot participants as well as
the other available participants.

## Main finding

The supplied root-level `../FORCe/` implementation takes a caller-sized matrix;
its wavelet decomposition and reconstruction use the actual array length. No
explicit 500-sample check or crop to the latest 100 ms appears in `FORCe.m`.
Its demo describes an adaptation by Johanna Wagner for window size/data length,
uses 500 Hz data, and calls the library on non-overlapping one-second windows.
The source comments describing a hard-coded one-second input and a 100-ms
output do not match the visible implementation. This is a static finding,
not a successful two-second execution test or validation of artifact removal.

The publication describes one-second cleaning windows and a two-level Sym4
decomposition. Therefore preserving the supplied code does not make a
two-second cleaning call identical to the published application. Keep the
duration of the analysis epoch separate from the duration of a cleaning call.

Primary paper: [author-uploaded manuscript](https://www.researchgate.net/publication/264868092_FORCe_Fully_Online_and_Automated_Artifact_Removal_for_Brain-Computer_Interfacing),
Methods II.A. Source baseline for this review: the locally supplied `../FORCe/`
folder, not a newly authenticated upstream release. Its acquisition/version
provenance still needs to be recorded before calling it a canonical release.

## Changes relative to the supplied root copy

| Change in active `Code/FORCe` | Effect | Needed for 1,000-sample input? | Source-preserving disposition |
|---|---|---|---|
| Optional diagnostics output | Reports removal/abort decisions; adapter rejects some statuses | No | Prefer external QC; retain instrumentation only as an explicit, tested patch if internal decisions are needed |
| Explicit decomposition depth and node selection; vector cell allocation | Generalizes beyond the supplied fixed depth of two; previous report found equivalence at depth two | No | Use supplied fixed-depth helper in the fidelity baseline |
| IC spike indexing and denominator change | Changes a rejection vote and potentially component removal | No | Keep in the historical corrected branch; exclude from a strict supplied-code baseline |
| FFT frequency-label correction and vector validation | Changes which bins enter frequency criteria; amplitude values are retained | No | Keep in historical corrected branch; do not silently include in supplied-code baseline |
| Assertions on undefined spectral/spike/IC features | Converts some undefined cases into failures and epoch rejection | No | External finite-input/output/error QC is possible; internal-feature QC requires instrumentation or a patched branch |
| Accelerometer-mode assertion | Explicitly rejects an unsupported mode | No | Enforce `useAcc=0` in the caller |
| `mi.m` MEX-name annotation | The supplied root copy already calls `hista__72_mex` correctly | No | Copy the supplied `mi.m`; do not claim that this root copy needs a function-name repair |
| `hista.m` byte difference | Git text comparison shows no content change; line endings differ | No | Use a byte-preserved supplied copy |

Byte-identical MATLAB files: `checkThresholds.m`, `demo.m`,
`estimateRemovedChs.m`, `extractFeaturesMultiChsWaveAMI.m`, `hist2a.m`,
`minf.m`, `removeArtifactsOnlineWavessobi.m`, and `sobi_FAST.m`.
The root-level source itself already differs from the paper in some criteria
(for example, disabled 1/f voting and an added high/low spectral ratio).
Those are inherited source/paper discrepancies, not necessarily our edits.
Do not resolve them by inventing new formulas while claiming source fidelity.

## Caller decisions that also matter

The current adapter rejects an epoch before cleaning if any channel exceeds
the supplied positive-only 200-microvolt threshold. This prevents the source's
interpolation branch from running. It is an explicit dataset QC policy, not
the supplied interpolation behavior. The final absolute 100-microvolt epoch
limit is a separate pipeline rejection rule.

The pipeline supplies high-passed microvolt data, forces symmetric wavelet
boundary extension, performs cleaning on the whole epoch, then low-passes and
baselines. These are caller settings and must be reported independently of
source edits. Original coordinates and their units matter for the inherited
interpolation formula; retaining its code does not validate its use with our
montage. No interpolation decision should be changed in this review.

Two-second windows change the number of observations used by SOBI, AMI lag
coverage, spectra and statistical thresholds even at the same decomposition
depth. For example, AMI lags run up to half the available coefficient length.
Longer input is consequently a methodological change, not just a storage-shape
change. The earlier reduction of the movement-onset join is useful evidence
about a boundary artifact, but does not validate physiological recovery.

## Recommended architecture and decision

1. Preserve `PRE_06` as the historical locally corrected result.
   Do not relabel it as an untouched-source result or overwrite it.
2. Retain an immutable copy of the supplied library with a SHA-256 manifest,
   license/author notices and provenance. Isolate its MATLAB path from the
   corrected library; avoid recursive path addition and check resolved names.
   Compiled histogram helpers also need their own provenance and verification.
3. Keep units, transposition, channel ordering, input/output checks, error
   capture, wavelet-mode restoration, epoch identities and dataset rejection
   rules in a small adapter. Call the supplied four-input, one-output API.
   Do not change spike votes, spectra, thresholds or depth to support 2 s.
4. Evaluate two separately named applications using the same supplied source:
   **one-second cleaning followed by two-second epoch extraction**, and
   **one supplied-code call per two-second epoch**. The first retains the
   documented cleaning duration but still needs boundary checks; the second
   retains source code but explicitly adapts window duration. Continuous
   one-second blocks do not eliminate joins; they avoid deliberately placing
   the join at movement onset for every trial. Neither option should be
   declared superior before comparison.
5. Before selecting an application, run a focused source compatibility check
   and a small matched pilot with common-trial comparisons, rejection reasons,
   onset/other-boundary steps, waveform amplitude and timing, and examples of
   artifacts and relatively clean data. Avoid selecting a method solely for
   a smoother or more recognizable ErrP waveform. Do not rerun the cohort yet.

Preferred starting point for the two-second requirement: the unchanged
supplied four-input implementation on the full epoch, behind the minimal
adapter, explicitly described as an offline two-second-window application.
Retain the one-second application as a source-faithful duration reference.
If strict conformity to the publication's duration is required, choose the
one-second cleaning application and then extract two-second analysis epochs.

Suggested wording after successful execution and evaluation: “EEG was cleaned
using the supplied FORCe implementation, applied offline to two-second
movement-locked epochs. The published method uses one-second windows; the
longer cleaning window was evaluated separately.” This states what was used
without implying that source preservation establishes validation.

## Verification status

Completed: source diffs, byte comparisons, active adapter/filter inspection,
published window/decomposition description, and review of saved pilot reports.

An isolated MATLAB probe is saved in `tmp/audit_force_source_windows.m`. It is
not a production adapter or a full pipeline test. MATLAB failed at startup in
the sandbox with a file-system inconsistency. The requested retry outside the
sandbox was declined. No runtime result, numerical equivalence or physiological
validation is claimed. No pipeline outputs were regenerated.
