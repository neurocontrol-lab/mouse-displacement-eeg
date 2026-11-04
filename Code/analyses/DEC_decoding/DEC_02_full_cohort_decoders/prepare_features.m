% DEC_02: Full-cohort decoders.
% Workflow, execution order and interpretation: README.md in this folder.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Full-cohort no-FORCe features using the saved v1 epochs.
% Reuse filtering/baselining, check raw quality across [-1.5,1.5), then
% retain every no-FORCe-accepted trial. No FORCe acceptance restriction.
root = project_root();
out = fullfile(root, 'output', 'DEC_decoding', 'DEC_02_full_cohort_decoders');
prepared = fullfile(out, 'prepared');
if ~isfolder(prepared)
    mkdir(prepared);
end
parsed = fullfile(root, 'output', 'PRE_preprocessing_artifacts', 'PRE_01_no_force_reference', 'parsed');
processed = fullfile(root, 'output', 'PRE_preprocessing_artifacts', 'PRE_01_no_force_reference', 'processed');
M = readtable(fullfile(parsed, 'manifest.csv'), 'TextType', 'string');
M = sortrows(M, {'subject','session','recordingDate','runNumber','run'});
writetable(M, fullfile(out, 'recording_inventory.csv'));
writetable(M(M.validTrials>0,:), fullfile(out, 'selected_manifest.csv'));
channels = {'P3','PO3','PO7','CP5','CP1','Cz','FCz','FC1'};
allF = cell(height(M),1);
allT = allF;
allQ = allF;
allR = allF;
allP = allF;
for f = 1:height(M)
    destination = fullfile(prepared, M.run(f) + '.mat');
    if isfile(destination)
        S = load(destination, 'F','T','Q','R','P');
        allF{f}=S.F;
        allT{f}=S.T;
        allQ{f}=S.Q;
        allR{f}=S.R;
        allP{f}=S.P;
        fprintf('%d/%d reused %s\n',f,height(M),M.run(f));
        continue;
    end
    p = load(fullfile(parsed, M.run(f)+'.mat'), 'trials','info');
    trials = p.trials;
    n = height(trials);
    cohort = "validation";
    if ismember(M.subject(f),["mle01","spe30"])
        cohort="pilot";
    end
    eligible = false(n,1);
    accepted = false(n,1);
    rejection = string(trials.reason);
    F = zeros(n,56);
    nr = 0;
    P = table();
    if M.validTrials(f)>0
        a = load(fullfile(processed,M.run(f)+'.mat'));
        assert(a.cfg.fs==500 && isequal(a.cfg.band,[1 20]) && a.cfg.filterOrder==4);
        assert(isequal(a.cfg.window,[-1 1]) && isequal(a.cfg.baseline,[-.2 0]));
        assert(a.cfg.maxAmplitudeUV==100 && a.cfg.lossGuardSeconds==2);
        assert(contains(string(a.processingNote),'no FORCe/ICA'));
        assert(isequal(a.channels,channels) && isequal(a.time(:),(-500:499)'/500));
        assert(isequal(trials.trial,a.trials.trial) && isequaln(trials.label,a.trials.label));
        raw = readmatrix(fullfile(root,'data',M.subject(f),M.run(f)+'.easy'),'FileType','text');
        assert(size(raw,2)==13 && size(raw,1)==p.info.samples);
        bad = raw(:,12)==255 | any(~isfinite(raw(:,1:8)),2);
        gap = find(diff(raw(:,13))~=2);
        bad(gap)=true;
        bad(gap+1)=true;
        edges = diff([false;~bad;false]);
        first=find(edges==1);
        last=find(edges==-1)-1;
        quality = true(size(bad));
        for j=1:numel(first)
            if last(j)-first(j)+1<=2000
                continue;
            end
            quality(first(j)+1000:last(j)-1000)=false;
        end
        for k=1:n
            if ~trials.valid(k)
                continue;
            end
            ix = trials.movementSample(k)+(-750:749);
            if min(ix)<1 || max(ix)>size(raw,1)
                rejection(k)="out_of_bounds";
                continue;
            end
            if any(quality(ix))
                rejection(k)="gap_or_filter_guard";
                continue;
            end
            eligible(k)=true;
            if ~a.trials.accepted(k)
                rejection(k)=string(a.trials.rejection(k));
                continue;
            end
            z = squeeze(a.epochs(k,:,:));
            assert(isequal(size(z),[1000 8]) && all(isfinite(z),'all'));
            assert(max(abs(z),[],'all')<=100);
            assert(max(abs(mean(z(401:500,:),1)))<1e-8);
            accepted(k)=true;
            rejection(k)="ok";
            nr=nr+1;
            F(nr,:) = reshape(mean(reshape(z(601:950,:),50,7,8),1),1,56);
        end
        % Verify cached v1 signals and acceptance against the saved pilot control.
        if cohort=="pilot"
            b = load(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis','processed',M.run(f)+'.mat'), ...
            'X','accepted','trials');
            assert(isequal(trials.trial,b.trials.trial));
            assert(isequal(accepted,b.accepted(:,1)));
            maxDifference=0;
            for k=find(accepted)'
                d=squeeze(a.epochs(k,:,:))-squeeze(b.X(k,:,:,1));
                maxDifference=max(maxDifference,max(abs(d),[],'all'));
            end
            assert(maxDifference<1e-8);
            P=table(M.subject(f),M.session(f),M.run(f),sum(accepted),maxDifference, ...
            'VariableNames',{'subject','session','run','accepted','maxDifferenceUV'});
        end
        clear raw a b;
    end
    F = F(1:nr,:);
    Q = table(repmat(M.subject(f),n,1),repmat(M.session(f),n,1), ...
    repmat(M.recordingDate(f),n,1),repmat(M.runNumber(f),n,1), ...
    repmat(M.run(f),n,1),trials.trial,trials.label,trials.valid,eligible,accepted,rejection, ...
    repmat(cohort,n,1),'VariableNames',{'subject','session','recordingDate','runNumber', ...
    'run','trial','label','eventValid','intervalEligible','accepted','rejection','cohort'});
    T = Q(accepted,{'subject','session','recordingDate','runNumber','run','trial','label','cohort'});
    R = table(M.subject(f),M.session(f),M.run(f),cohort,n,sum(trials.valid),sum(eligible), ...
    sum(accepted),sum(accepted & trials.label==1),sum(accepted & trials.label==2), ...
    'VariableNames',{'subject','session','run','cohort','trialRows','eventValid','intervalEligible', ...
    'accepted','acceptedND','acceptedD'});
    save(destination,'F','T','Q','R','P','-v7');
    allF{f}=F;
    allT{f}=T;
    allQ{f}=Q;
    allR{f}=R;
    allP{f}=P;
    fprintf('%d/%d %s: %d/%d accepted, %s\n',f,height(M),M.run(f),nr,n,cohort);
end
features=vertcat(allF{:});
T=vertcat(allT{:});
Q=vertcat(allQ{:});
R=vertcat(allR{:});
P=vertcat(allP{:});
assert(size(features,1)==height(T) && all(isfinite(features),'all'));
assert(height(unique(T(:,{'run','trial'})))==height(T));
assert(all(ismember(T.label,[1 2])));
fs=500;
binStart=.2+(0:6)/10;
binEnd=binStart+.1;
save(fullfile(out,'features.mat'),'features','channels','fs','binStart','binEnd','-v7');
writetable(T,fullfile(out,'trial_metadata.csv'));
writetable(Q,fullfile(out,'trial_quality.csv'));
writetable(R,fullfile(out,'retention_by_run.csv'));
writetable(P,fullfile(out,'pilot_cache_verification.csv'));
fprintf('FEATURE PREPARATION COMPLETE: %d participants, %d accepted trials, 56 features\n', ...
numel(unique(M.subject)),height(T));
