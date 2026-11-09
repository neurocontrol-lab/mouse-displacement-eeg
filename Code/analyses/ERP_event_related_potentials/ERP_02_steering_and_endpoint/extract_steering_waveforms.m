function extract_steering_waveforms()
% Re-index saved no-FORCe EEG on the AUD_02 jump and steering times.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
cfg = dataset_config();
reference = experiment_paths('PRE_01');
out = experiment_paths('ERP_02');
scratch = fullfile(out.result,'tmp');
if ~isfolder(scratch), mkdir(scratch); end

T = readtable(fullfile(out.result,'trial_selection.csv'),'TextType','string');
P = readtable(fullfile(out.result,'steering_pairs.csv'),'TextType','string');
windows = jsondecode(fileread(fullfile(out.result,'windows.json')));
channels = cfg.channels;
subjects = sort(unique(T.subject));
sessions = string(cfg.sessions);
jumpSamples = -250:249;
steerSamples = -500:249;
jumpMs = jumpSamples*1000/cfg.fs;
steerMs = steerSamples*1000/cfg.fs;
mask = cell(numel(windows),1);
electrodes = cell(numel(windows),1);
for w = 1:numel(windows)
    window = windows(w);
    mask{w} = jumpMs >= window.start_ms & jumpMs < window.end_ms_exclusive;
    [found,electrodes{w}] = ismember(string(window.electrodes),string(channels));
    assert(all(found) && sum(mask{w}) == (window.end_ms_exclusive-window.start_ms)*cfg.fs/1000);
end

% Jump: sample, channel, class (control/early), control subset (all/late/none), participant, session.
jumpSum = zeros(numel(jumpSamples),numel(channels),2,3,numel(subjects),numel(sessions));
pairCounts = zeros(3,numel(subjects),numel(sessions));
% Compare both alignments on exactly the same steering-detected trials.
steerSum = zeros(numel(steerSamples),numel(channels),numel(subjects),numel(sessions));
steerJumpSum = zeros(numel(jumpSamples),numel(channels),numel(subjects),numel(sessions));
steerCounts = zeros(numel(subjects),numel(sessions));
features = nan(height(T),numel(windows));

runs = unique(T.run,'stable');
for r = 1:numel(runs)
    rows = find(T.run==runs(r));
    B = T(rows,:);
    a = load(fullfile(reference.result,'processed',runs(r)+'.mat'), ...
        'epochs','trials','time','channels','processingNote','cfg');
    assert(isequal(a.time(:),(-500:499)'/cfg.fs) && isequal(a.channels,channels));
    assert(contains(string(a.processingNote),'no FORCe/ICA'));
    assert(a.cfg.fs==cfg.fs && isequal(a.cfg.band,[1 20]) && a.cfg.filterOrder==4 ...
        && isequal(a.cfg.baseline,[-.2 0]));
    [found,idx] = ismember(B.trial,a.trials.trial);
    assert(all(found) && all(a.trials.valid(idx) & a.trials.accepted(idx) & a.trials.label(idx)==2));
    assert(all(a.trials.displacementSample(idx)-a.trials.movementSample(idx)==B.jump_delay_samples));
    assert(all(isfinite(a.epochs(idx,:,:)),'all'));
    assert(max(abs(mean(a.epochs(idx,401:500,:),2)),[],'all')<1e-8);
    [~,s] = ismember(B.subject(1),subjects);
    [~,v] = ismember(B.session(1),sessions);
    aligned = zeros(numel(jumpSamples),numel(channels),height(B));
    for k = 1:height(B)
        aligned(:,:,k) = squeeze(a.epochs(idx(k),501+B.jump_delay_samples(k)+jumpSamples,:));
        for w = 1:numel(windows)
            features(rows(k),w) = mean(aligned(mask{w},electrodes{w},k),'all');
        end
        if B.steering_eeg_eligible(k)
            offset = B.steering_offset_samples(k);
            assert(offset>=0 && offset<=250);
            steerSum(:,:,s,v) = steerSum(:,:,s,v)+squeeze(a.epochs(idx(k),501+offset+steerSamples,:));
            steerJumpSum(:,:,s,v) = steerJumpSum(:,:,s,v)+aligned(:,:,k);
            steerCounts(s,v) = steerCounts(s,v)+1;
        end
    end
    pairs = P(P.run==runs(r),:);
    [foundA,early] = ismember(pairs.trial_early,B.trial);
    [foundB,control] = ismember(pairs.trial_control,B.trial);
    assert(all(foundA & foundB));
    assert(all(B.steering_250(early)=="early" & B.steering_250(control)==pairs.control_group));
    assert(all(B.side(early)==B.side(control) & B.side(early)==pairs.side));
    for k = 1:height(pairs)
        traces = aligned(:,:,[control(k),early(k)]);
        subset = 2 + (pairs.control_group(k)=="not_detected");
        for g = [1 subset]
            jumpSum(:,:,:,g,s,v) = jumpSum(:,:,:,g,s,v)+traces;
            pairCounts(g,s,v) = pairCounts(g,s,v)+1;
        end
    end
    if mod(r,50)==0 || r==numel(runs)
        fprintf('ERP_02 %d/%d recordings checked\n',r,numel(runs));
    end
end
assert(sum(pairCounts(1,:,:),'all')==height(P) && all(isfinite(features),'all'));
assert(isequal(pairCounts(1,:,:),pairCounts(2,:,:)+pairCounts(3,:,:)));
assert(sum(steerCounts,'all')==sum(T.steering_eeg_eligible));
subjects = cellstr(subjects);
sessions = cellstr(sessions);
save(fullfile(scratch,'waveform_sums.mat'),'jumpSum','pairCounts','steerSum','steerJumpSum', ...
    'steerCounts','features','channels','subjects','sessions','jumpMs','steerMs','-v7');
fprintf('ERP_02 extracted %d matched pairs and %d steering-aligned trials\n',height(P),sum(steerCounts,'all'));
end
