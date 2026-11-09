function extract_matched_waveforms()
% ERP_01: Re-index saved no-FORCe epochs at movement and target displacement.
% Match within recordings on pre-displacement reaction time, without EEG.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
cfg = dataset_config();
reference = experiment_paths('PRE_01');
decoder = experiment_paths('DEC_02');
out = experiment_paths('ERP_01');
scratch = fullfile(out.result,'tmp');
if ~isfolder(scratch), mkdir(scratch); end

T = readtable(fullfile(decoder.result,'trial_metadata.csv'),'TextType','string');
assert(height(unique(T(:,{'run','trial'}))) == height(T));
subjects = sort(unique(T.subject));
sessions = string(cfg.sessions);
channels = cfg.channels;
fs = cfg.fs;
moveSamples = -250:449;
jumpSamples = -250:249;
windows = jsondecode(fileread(fullfile(fileparts(mfilename('fullpath')),'windows.json')));
sampleGrid = struct('movement',moveSamples*1000/fs,'jump',jumpSamples*1000/fs);
windowSamples = cell(numel(windows),1);
windowChannels = cell(numel(windows),1);
for w = 1:numel(windows)
    def = windows(w);
    time = sampleGrid.(def.alignment);
    windowSamples{w} = time>=def.start_ms & time<def.end_ms_exclusive;
    [found,windowChannels{w}] = ismember(string(def.electrodes),string(channels));
    assert(all(found) && sum(windowSamples{w})==(def.end_ms_exclusive-def.start_ms)*fs/1000);
end
% Dimensions: time, channel, class (ND/D), delay set (all/short/long),
% participant, session. Each set has equal class counts.
moveSum = zeros(numel(moveSamples),numel(channels),2,3,numel(subjects),numel(sessions));
jumpSum = zeros(numel(jumpSamples),numel(channels),2,3,numel(subjects),numel(sessions));
counts = zeros(3,numel(subjects),numel(sessions));
runs = unique(T.run,'stable');
runPairs = cell(numel(runs),1);
runDeltas = nan(numel(runs),numel(windows));
for r = 1:numel(runs)
    rows = sortrows(T(T.run==runs(r),:),'trial');
    a = load(fullfile(reference.result,'processed',runs(r)+'.mat'), ...
        'epochs','trials','time','channels','processingNote','cfg');
    assert(isequal(a.time(:),(-500:499)'/fs) && isequal(a.channels,channels));
    assert(contains(string(a.processingNote),'no FORCe/ICA'));
    assert(a.cfg.fs==fs && isequal(a.cfg.band,[1 20]) && a.cfg.filterOrder==4 ...
        && isequal(a.cfg.baseline,[-.2 0]));
    [found,index] = ismember(rows.trial,a.trials.trial);
    assert(all(found) && all(a.trials.valid(index) & a.trials.accepted(index)));
    assert(isequal(rows.label,a.trials.label(index)));
    event = a.trials(index,:);
    assert(all(isfinite(a.epochs(index,:,:)),'all'));
    assert(max(abs(mean(a.epochs(index,401:500,:),2)),[],'all')<1e-8);
    nd = find(rows.label==1);
    d = find(rows.label==2);
    assert(numel(nd)+numel(d)==height(rows));
    assert(all(isnan(event.displacementSample(nd))));
    if isempty(nd) || isempty(d), continue; end

    rt = event.movementSample - event.targetSample;
    assert(all(isfinite(rt) & rt>0));
    cost = abs(rt(d)-rt(nd)');
    pairs = matchpairs(cost,max(cost,[],'all')+1);
    assert(size(pairs,1)==min(numel(nd),numel(d)));
    d = d(pairs(:,1));
    nd = nd(pairs(:,2));
    delay = event.displacementSample(d)-event.movementSample(d);
    assert(all(delay>0 & delay+max(jumpSamples)<=499));

    % Compare the shortest and longest equal-sized halves within each run.
    % Ties are ordered by D trial ID. An odd middle pair enters only the full mean.
    [~,order] = sortrows([delay rows.trial(d)]);
    half = floor(numel(delay)/2);
    group = repmat("middle",numel(delay),1);
    group(order(1:half)) = "short";
    group(order(end-half+1:end)) = "long";
    [~,s] = ismember(rows.subject(1),subjects);
    [~,v] = ismember(rows.session(1),sessions);
    runSums = struct('movement',zeros(numel(moveSamples),numel(channels)), ...
        'jump',zeros(numel(jumpSamples),numel(channels)));
    for k = 1:numel(delay)
        indices = index([nd(k),d(k)]);
        movement = permute(a.epochs(indices,501+moveSamples,:),[2 3 1]);
        % ND receives the exact D delay from its own movement onset.
        jump = permute(a.epochs(indices,501+delay(k)+jumpSamples,:),[2 3 1]);
        runSums.movement = runSums.movement+movement(:,:,2)-movement(:,:,1);
        runSums.jump = runSums.jump+jump(:,:,2)-jump(:,:,1);
        sets = [true group(k)=="short" group(k)=="long"];
        for subset = find(sets)
            moveSum(:,:,:,subset,s,v) = moveSum(:,:,:,subset,s,v)+movement;
            jumpSum(:,:,:,subset,s,v) = jumpSum(:,:,:,subset,s,v)+jump;
        end
        counts(:,s,v) = counts(:,s,v)+sets';
    end
    for w = 1:numel(windows)
        values = runSums.(windows(w).alignment);
        runDeltas(r,w) = mean(values(windowSamples{w},windowChannels{w}),'all')/numel(delay);
    end
    P = rows(d,{'subject','session','cohort','run'});
    P.trialD = rows.trial(d);
    P.trialND = rows.trial(nd);
    P.reactionD_ms = rt(d)*1000/fs;
    P.reactionND_ms = rt(nd)*1000/fs;
    P.delay_ms = delay*1000/fs;
    P.jumpSampleD = event.displacementSample(d);
    P.pseudoJumpSampleND = event.movementSample(nd)+delay;
    P.delayGroup = group;
    runPairs{r} = P;
    if mod(r,25)==0 || r==numel(runs)
        fprintf('ERP_01 %d/%d recordings checked\n',r,numel(runs));
    end
end
pairs = vertcat(runPairs{~cellfun(@isempty,runPairs)});
assert(height(pairs)==sum(counts(1,:,:),'all'));
assert(height(unique(pairs(:,{'run','trialD'})))==height(pairs));
assert(height(unique(pairs(:,{'run','trialND'})))==height(pairs));
assert(isequal(counts(2,:,:),counts(3,:,:)));
writetable(pairs,fullfile(out.result,'matched_trials.csv'));
moveMs = moveSamples*1000/fs;
jumpMs = jumpSamples*1000/fs;
subjects = cellstr(subjects);
sessions = cellstr(sessions);
hasPairs = ~cellfun(@isempty,runPairs);
runNames = cellstr(runs(hasPairs));
runDeltas = runDeltas(hasPairs,:);
save(fullfile(scratch,'waveform_sums.mat'),'moveSum','jumpSum','counts', ...
    'subjects','sessions','channels','moveMs','jumpMs','runNames','runDeltas','-v7');
fprintf('ERP_01 matched %d pairs from %d accepted trials\n',height(pairs),height(T));
end
