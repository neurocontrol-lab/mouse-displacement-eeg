# Search for the original RunResults generator

9 September 2026. The original generator was not found in the available project or supplied archives.

Searched local MATLAB/Python/notebook source, including hidden/ignored files, for RunResults creation, assignments to typ/pos/Labels/CleanTrials, FORCe calls and trigger parsing. Inspected the entry lists of ErrpAnalysis.zip (410 entries), EEG_tDCS.tar (1274 entries) and the manuscript ZIP; scanned candidate text source within the archives without extracting large datasets.

Findings:
- Code/tDCsErrPotential.m and the root tDCsErrPotential.m load existing RunResults structs; neither generates them. Their FORCe sections are comments.
- EEG_tDCS.tar contains only one candidate source script: data/spe30/trialextraction.m, also available in the extracted data directory.
- That script extracts separate one-second fixation and movement epochs, uses 0/1 labels, and never creates RunResults or runs filtering/FORCe. It keeps all nonzero triggers, so it is not the zero-to-nonzero parser whose output matches the saved MAT. It nevertheless has a related fragility: the next nonzero event after 400 must be 100 or 500, otherwise it aborts, including when that next event is 255.
- The archive source search found no assignments generating RunResults.typ/pos/Labels/CleanTrials and no active FORCe implementation responsible for these saved files.

The missing material to request from the original analyst is the script/function that reads *.easy, constructs the four-second movement-locked epochs, generates RunResults.pos/typ/Labels, applies filtering and FORCe, and writes cleanErrPotData/<subject>/*_EEG.mat, plus its dependencies and version/settings. Feature extraction/classification is a later stage and exists in tDCsErrPotential.m; the known marker omission is in event parsing/label creation.

Until the generator is recovered, its exact source-level defect cannot be cited. Its event-parser behaviour has been reconstructed from stored output, and a replacement metadata parser can be written and validated independently. No original data or analysis scripts were modified by this search.
