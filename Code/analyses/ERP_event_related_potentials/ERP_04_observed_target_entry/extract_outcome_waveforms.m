function extract_outcome_waveforms()
% ERP_04: Align matched pairs to the logged jump or the paired pseudo-jump.
code = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
addpath(code,fullfile(code,'helpers'));
out = experiment_paths('ERP_04');
scratch = fullfile(out.result,'tmp');
if ~isfolder(scratch), mkdir(scratch); end
P = readtable(fullfile(out.result,'matched_pairs.csv'),'TextType','string');
[waveformSums,pairCounts,channels,subjects,sessions,jumpMs,contrasts] = extract_paired_jump_waveforms(P);
save(fullfile(scratch,'waveform_sums.mat'),'waveformSums','pairCounts','channels','subjects','sessions','jumpMs','contrasts','-v7');
fprintf('ERP_04 extracted %d pairs across %d recordings\n',height(P),numel(unique(P.run)));
end
