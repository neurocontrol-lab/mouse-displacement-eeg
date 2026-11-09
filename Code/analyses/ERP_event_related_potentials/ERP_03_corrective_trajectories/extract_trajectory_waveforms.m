function extract_trajectory_waveforms()
% Reuse the saved PRE_01 epochs and align each matched D trial to EEG marker 500.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
cfg = dataset_config();
reference = experiment_paths('PRE_01');
out = experiment_paths('ERP_03');
scratch = fullfile(out.result,'tmp');
if ~isfolder(scratch), mkdir(scratch); end
P = readtable(fullfile(out.result,'matched_pairs.csv'),'TextType','string');

channels = cfg.channels;
subjects = sort(unique(P.subject));
sessions = string(cfg.sessions);
jumpSamples = -250:249;
jumpMs = jumpSamples * 1000 / cfg.fs;
waveformSums = zeros(numel(jumpSamples),numel(channels),2,numel(subjects),numel(sessions));
pairCounts = zeros(numel(subjects),numel(sessions));
runs = unique(P.run,'stable');
for r = 1:numel(runs)
    pairs = P(P.run==runs(r),:);
    a = load(fullfile(reference.result,'processed',runs(r)+'.mat'), ...
        'epochs','trials','time','channels','processingNote','cfg');
    assert(cfg.fs==500 && isequal(a.time(:),(-500:499)'/cfg.fs) && isequal(a.channels,channels));
    assert(contains(string(a.processingNote),'no FORCe/ICA'));
    assert(a.cfg.fs==cfg.fs && isequal(a.cfg.band,[1 20]) && a.cfg.filterOrder==4 ...
        && isequal(a.cfg.baseline,[-.2 0]));
    [~,s] = ismember(pairs.subject(1),subjects);
    [~,v] = ismember(pairs.session(1),sessions);
    trialIds = [pairs.erroneous_trial pairs.corrective_trial];
    offsets = [pairs.erroneous_jump_samples pairs.corrective_jump_samples];
    [found,idx] = ismember(trialIds,a.trials.trial);
    assert(all(found,'all') && numel(unique(idx))==numel(idx));
    assert(all(a.trials.valid(idx) & a.trials.accepted(idx) & a.trials.label(idx)==2,'all'));
    savedOffsets = a.trials.displacementSample(idx(:))-a.trials.movementSample(idx(:));
    assert(isequal(savedOffsets,offsets(:)));
    assert(all(isfinite(a.epochs(idx(:),:,:)),'all'));
    assert(max(abs(mean(a.epochs(idx(:),401:500,:),2)),[],'all')<1e-8);
    for c = 1:2
        for k = 1:height(pairs)
            samples = 501 + offsets(k,c) + jumpSamples;
            waveformSums(:,:,c,s,v) = waveformSums(:,:,c,s,v) + squeeze(a.epochs(idx(k,c),samples,:));
        end
    end
    pairCounts(s,v) = pairCounts(s,v) + height(pairs);
end
assert(sum(pairCounts,'all')==height(P));
subjects = cellstr(subjects);
sessions = cellstr(sessions);
save(fullfile(scratch,'waveform_sums.mat'),'waveformSums','pairCounts','channels','subjects','sessions','jumpMs','-v7');
fprintf('ERP_03 extracted %d pairs from %d recordings\n',height(P),numel(runs));
end
