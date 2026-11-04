# Event verification and figure reproduction plan

Audited 9 September 2026. Original recordings and MATLAB files were not modified.

## Updated next actions after epoch verification

Use `event_codes.md` as the current event reference; it supersedes the initial uncertainty about 255 below. Code 255 denotes data loss. Working subject mapping agreed with the user: S1=spe30, S2=mle01. Run-local epochs 76/78 in mle01 retest_run3 are now waveform-matched to the corresponding raw trials; see `epoch_mapping_confirmation.md`. Both must carry condition label 2. No labels have yet been modified.

1. Locate the generating event parser, or implement a documented replacement if unavailable. Recognize 255-to-500 and other distinct task-code transitions; retain quality flags separately and preserve continuous sample indices. Verify with focused cases for normal events, 255-to-500, repeated marker samples and incomplete trials.
2. Rebuild event/trial metadata for all S1/S2 runs and compare against mouse-log trial numbers, target jumps and existing epoch positions. Report every changed class, missing event, ambiguous trial and exclusion. Do not restrict the repair to the two known errors; a target-onset marker was also omitted in the affected run.
3. Save corrected per-run outputs separately with a change log. For the verified run, Labels(76) and Labels(78) should change from 1 to 2; regenerate typ/pos consistently. Assess data-loss overlap before declaring these epochs fit for analysis. Correct condition does not imply acceptable EEG quality.
4. Trace run order and retained-epoch indices into S2Labels and its corresponding trial tensor, then rebuild aligned subject-level outputs. Do not use run-local indices 76/78 directly on the aggregate. Reconcile other dropped trials and S1's run-count discrepancy.
5. Continue with preprocessing verification and Figures 2/3, then Figure 4 and Figure 5 as detailed below. There is no need to rerun expensive EEG cleaning solely to repair class metadata if epoch correspondence and quality are established; rerun extraction/cleaning where an audit shows that boundaries or retained data must change.

## Verified file layout and event interpretation

The `.easy` recordings have 13 columns: eight EEG channels, three accelerometer channels, trigger (column 12; Python index 11), and timestamp in milliseconds (column 13). The inspected `.info` specifies 500 Hz and EEG units of nV. Convert raw EEG to microvolts by dividing by 1000; do not convert already-scaled cleaned arrays again. Channel order: P3, PO3, PO7, CP5, CP1, Cz, FCz, FC1.

| Code | Interpretation | Evidence and confidence |
|---|---|---|
| 100 | Start of a new trial / return-to-start phase | Mouse CSV trial number increments at this event; not a correctness label. |
| 200 | Preparation/fixation cue, likely fixation-cross onset | Sequence and stationary start position fit the protocol. Exact display action remains provisional without stimulus code or meeting confirmation. |
| 300 | Initial target onset | Mouse target coordinates change to the central target; extraction script also uses this event for the preceding fixation epoch. |
| 400 | Movement-onset marker | Explicitly used for movement epochs in `data/spe30/trialextraction.m`; mouse begins leaving starting position. |
| 500 | Target-displacement marker | Mouse target x changes by 400 pixels; extraction script uses this to identify error/displaced trials. |

Normal task sequences: `100 200 300 400` (non-displaced) and `100 200 300 400 500` (displaced). Label within trial boundaries. A new 100 closes the preceding trial; it does not itself mean correct. Code 255 also occurs in the raw trigger channel; its meaning is unverified. Preserve and flag it, and do not use it as a task event or assume the next nonzero trigger is a class marker. Validate event counts/order and mark incomplete/ambiguous trials separately. A terminal trial without a subsequent 100 requires independent completion evidence from the mouse log.

The small extraction script uses labels 0=correct, 1=error. Saved RunResults and the later analysis use 1=correct, 2=error. Here “error” means target displaced, not necessarily failure to reach the target.

## Audit results and blockers

The script audits all run-named `.easy` files under spe30 and mle01, excluding training and stimulation-only files. Outputs are `runs.json` and `trials.csv`; sample positions in the CSV are MATLAB-compatible, one-based. Classification from raw markers is provisional where a trial has anomalies.

| Folder | Run files | Movement trials | Saved per-run trial total | Recorded 400-to-500 delay, min / median / max |
|---|---:|---:|---:|---|
| spe30 | 21 | 2100 | 2099 | 4 / 84 / 464 ms |
| mle01 | 15 | 1496 | 1494 | 30 / 70 / 424 ms |

The paper reports S1=2306 retained trials and S2=1494. Counts and scripts suggest spe30=S1 and mle01=S2, but the identity mapping is not conclusively established. Available spe30 non-training runs do not account for the paper's S1 total. Check whether training runs were included, other sessions are missing, or saved aggregates use a different manifest. Do not add training runs merely to force the count.

Four runs fail exact raw-vs-saved label-vector comparison. Three have fewer saved epochs than movement events: spe30 pre_run3 on 20180717 (99 vs 100), mle01 post_run3 on 20181112 (99 vs 100), and mle01 retest_run4 on 20181113 (99 vs 100). These may reflect rejected trials; recover the exclusion/index mapping before treating them as errors.

The fourth run, `20181113091555_mle01_retest_run3_EEG`, has 100 saved and 100 raw movement trials, but trials 76 and 78 are saved as label 1 despite both EEG and matching mouse CSV containing code 500. The mouse CSV explicitly changes the target from x=508 to x=108 on those trials. Reconcile this with saved epoch provenance before correcting derived labels. No labels have been changed.

The recorded delays conflict with the short paper's claim of at most 6 ms between movement and displacement. For example, mle01 pre_run1 trial 2 has about 48 ms in both EEG and mouse timestamps. These are marker intervals, not independently measured screen-display latency. Obtain stimulus source/timing definitions before claiming the two events are simultaneous. Reproduce the paper with t=0 at 400, and retain 500 timing for later displacement-locked analyses.

The GA_data S1/S2 `extractedData` files contain averaged waveforms (eight channel structures with timeVector, GACorrect, GAError, GADifference), not single-trial features. Their vectors have 1001 points. Per-run CleanTrials inspected have 2000 samples at 500 Hz (four seconds); the paper's final window is two seconds / 1000 points. Determine the exact event index and endpoint convention before cropping. The HDF5-based aggregate S1/S2 arrays were not read successfully with the installed library; per-run MAT files were inspected instead.

## Ordered action plan

1. **Freeze provenance and trial metadata.** Establish S1/S2 identity and included runs; reconcile all exclusions and the two contradictory labels. Build one row per epoch containing subject, session, run, original trial, class, 300/400/500 positions, rejection status and reason. Match metadata length and order to each saved tensor. Gate: no unresolved epoch-to-label mapping.
2. **Verify preprocessing and timing once.** Recover original filter order, phase handling, FORCe implementation, units, baseline convention, and epoch event index. The paper specifies Butterworth 1–20 Hz, FORCe, DC removal and rejection above 100 microvolts. Existing analysis additionally subtracts the first sample; document whether this produced the published curves. Preserve a faithful reproduction and record deliberate corrections separately. Gate: correct 500 Hz time axis, 400 at zero, validated channels, and a documented 1000-vs-1001 endpoint choice.
3. **Reproduce Figures 2 and 3 first.** Plot each subject's eight-channel correct and displaced averages and Error−Correct difference over [-1,1] s. Show zero and 0.5 s reference lines. Recompute per-sample two-sided unpaired tests on trials with the paper's Bonferroni threshold 0.05/8000=0.00000625 when using 8000 comparisons. Existing MATLAB versions contain incorrect thresholds and tests on individual averaged scalars; do not copy those significance calculations. Compare numerical waveforms with saved GA_data as well as paper images, and record retained class counts.
4. **Reproduce Figure 4.** Plot Error−Correct at the stated S1 times 654/504 ms and S2 times 726/496 ms. Verify polarity, channel coordinates, reference and colour scale. Only eight electrodes were measured: do not represent unrecorded electrodes as measured zeros. Document any difference from the published interpolation. Figure 1 is a protocol schematic, not an EEG-derived result; redraw only after event semantics are settled.
5. **Extract features and reproduce Figure 5.** Use single-trial spatiotemporal amplitudes from the validated epoch. The paper specifies a decision tree, 10-fold CV, and 100 features ranked by r-squared using training trials only. Saved MATLAB classification sections instead use other settings (including quadratic discriminant analysis and leave-one-out CV), so they are not a faithful Figure 5 implementation. Save fold assignments/seed; perform feature selection inside each fold; report overall accuracy and each class's recall with mean/SD across folds. If original folds/tree settings cannot be recovered, label the result a methodological reproduction rather than an exact numerical match. Report the majority-class baseline alongside the paper's plotted reference line.
6. **Then extend the scientific analysis.** Compare movement- and displacement-locked responses, stratify sessions/conditions and reaction times, use run-separated validation, and expand to remaining subjects after S1/S2 provenance and figure checks pass. These are follow-up analyses, not prerequisites for plotting validated descriptive averages.

## Source scope

Primary sources: `GBCIC2024_paper_97.pdf` (methods and Figures 1–5), `.info` recording metadata, raw EEG and matching mouse logs, `data/spe30/trialextraction.m`, both `tDCsErrPotential.m` versions, and saved per-run RunResults. The older proof was text-extracted and consulted for protocol context. The meeting MP3 has not been transcribed/listened to in this audit; no conclusions here are attributed to the meeting or to reviewer feedback. The supplied papers do not establish why the work was rejected.
