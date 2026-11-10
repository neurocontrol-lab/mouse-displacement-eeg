function [waveformSums,pairCounts,channels,subjects,sessions,jumpMs,contrasts] = extract_paired_jump_waveforms(P)
% Read saved PRE_01 epochs and sum the paired jump or pseudo-jump traces.
cfg = dataset_config();
reference = experiment_paths('PRE_01');
channels = cfg.channels;
subjects = sort(unique(P.subject));
sessions = string(cfg.sessions);
jumpSamples = -250:249;
jumpMs = jumpSamples * 1000 / cfg.fs;
contrasts = unique(P.contrast,'stable');
waveformSums = zeros(numel(jumpSamples),numel(channels),2,numel(contrasts),numel(subjects),numel(sessions));
pairCounts = zeros(numel(contrasts),numel(subjects),numel(sessions));
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
    trialIds = [pairs.reference_trial pairs.comparison_trial];
    offsets = [pairs.reference_jump_samples pairs.comparison_jump_samples];
    labels = [pairs.reference_label pairs.comparison_label];
    [found,idx] = ismember(trialIds,a.trials.trial);
    assert(all(found,'all'));
    assert(all(a.trials.valid(idx(:)) & a.trials.accepted(idx(:))));
    assert(isequal(a.trials.label(idx(:)),labels(:)));
    savedOffsets = a.trials.displacementSample(idx(:))-a.trials.movementSample(idx(:));
    flatOffsets = offsets(:);
    assert(isequal(savedOffsets(labels(:)==2),flatOffsets(labels(:)==2)));
    assert(all(isnan(savedOffsets(labels(:)==1))));
    assert(all(offsets>0 & offsets<=250,'all'));
    used = unique(idx(:));
    assert(all(isfinite(a.epochs(used,:,:)),'all'));
    assert(max(abs(mean(a.epochs(used,401:500,:),2)),[],'all')<1e-8);
    [~,contrastIds] = ismember(pairs.contrast,contrasts);
    for c = unique(contrastIds)'
        use = contrastIds==c;
        pairTrials = idx(use,:);
        assert(numel(unique(pairTrials))==numel(pairTrials));
        for k = find(use)'
            for g = 1:2
                samples = 501 + offsets(k,g) + jumpSamples;
                waveformSums(:,:,g,c,s,v) = waveformSums(:,:,g,c,s,v) + squeeze(a.epochs(idx(k,g),samples,:));
            end
        end
        pairCounts(c,s,v) = pairCounts(c,s,v) + nnz(use);
    end
end
assert(sum(pairCounts,'all')==height(P));
subjects = cellstr(subjects);
sessions = cellstr(sessions);
contrasts = cellstr(contrasts);
end
