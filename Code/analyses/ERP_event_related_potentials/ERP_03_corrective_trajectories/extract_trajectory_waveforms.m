function extract_trajectory_waveforms()
% ERP_03: Align each matched displaced trial to EEG marker 500.
code = fileparts(fileparts(fileparts(fileparts(mfilename('fullpath')))));
addpath(code,fullfile(code,'helpers'));
out = experiment_paths('ERP_03');
scratch = fullfile(out.result,'tmp');
if ~isfolder(scratch), mkdir(scratch); end
P = readtable(fullfile(out.result,'matched_pairs.csv'),'TextType','string');
P = renamevars(P,{'erroneous_trial','corrective_trial','erroneous_jump_samples','corrective_jump_samples'}, ...
    {'reference_trial','comparison_trial','reference_jump_samples','comparison_jump_samples'});
P.contrast = repmat("trajectory",height(P),1);
P.reference_label = repmat(2,height(P),1);
P.comparison_label = P.reference_label;
[waveformSums,pairCounts,channels,subjects,sessions,jumpMs] = extract_paired_jump_waveforms(P);
waveformSums = reshape(waveformSums,numel(jumpMs),numel(channels),2,numel(subjects),numel(sessions));
pairCounts = reshape(pairCounts,numel(subjects),numel(sessions));
save(fullfile(scratch,'waveform_sums.mat'),'waveformSums','pairCounts','channels','subjects','sessions','jumpMs','-v7');
fprintf('ERP_03 extracted %d pairs from %d recordings\n',height(P),numel(unique(P.run)));
end
