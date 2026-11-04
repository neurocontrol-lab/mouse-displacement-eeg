% Stage 3: participant/session condition averages and diagnostic plots.
% Inputs: stage-2 processed epochs, selected strictly by trials.accepted.
% Outputs: condition means, displaced-minus-non-displaced differences,
% trial metadata, PNG/MAT figures and session_counts.csv.
% Two-sided equal-variance trial-level t-tests use Bonferroni correction
% within each participant/session (8 channels x 1000 samples).
pipelineDir=fileparts(mfilename('fullpath'));
codeDir=fileparts(pipelineDir);
addpath(codeDir,pipelineDir,fullfile(codeDir,'helpers'));
if ~exist('cfg','var') || ~isstruct(cfg) || ~isfield(cfg,'experimentId')
    cfg=config('PRE_06');
end
out=fullfile(cfg.output,'figures','by_session'); if ~isfolder(out), mkdir(out); end
summary=table();
selected=readtable(fullfile(cfg.output,'selected_manifest.csv'),'TextType','string');
for s=1:numel(cfg.subjects)
  for ss=1:numel(cfg.sessions)
    session=cfg.sessions{ss};
    files=dir(fullfile(cfg.output,'processed',['*_' cfg.subjects{s} '_' session '_run*_EEG.mat']));
    files=files(ismember(string({files.name}),selected.run+".mat"));
    X=[]; labels=[]; trialMetadata=table();
    for f=1:numel(files)
        d=load(fullfile(files(f).folder,files(f).name)); keep=d.trials.accepted;
        assert(strcmp(d.info.session,session),'Session mismatch in %s',files(f).name);
        X=cat(1,X,d.epochs(keep,:,:)); labels=[labels;d.trials.label(keep)]; %#ok<AGROW>
        trialMetadata=[trialMetadata;d.trials(keep,:)]; %#ok<AGROW>
    end
    summary=[summary;table(string(cfg.subjects{s}),string(session),numel(files),sum(labels==1),sum(labels==2),...
        'VariableNames',{'subject','session','runFiles','nonDisplaced','displaced'})]; %#ok<AGROW>
    if sum(labels==1)<2 || sum(labels==2)<2
        warning('Too few retained trials for %s %s; skipping plot',cfg.subjects{s},session); continue;
    end
    fprintf('Plotting %s / %s: %d trials\n',cfg.subjects{s},session,numel(labels));
    correct=squeeze(mean(X(labels==1,:,:),1)); displaced=squeeze(mean(X(labels==2,:,:),1));
    difference=displaced-correct; p=nan(size(correct));
    for ch=1:8
        [~,p(:,ch)]=ttest2(X(labels==1,:,ch),X(labels==2,:,ch),'Dim',1,'Vartype','equal');
    end
    significant=p<cfg.alpha/numel(p);
    fig=figure('Visible','off','Position',[100 100 1100 1000]); tiledlayout(4,2);
    for ch=1:8
        nexttile; h=plot(d.time,correct(:,ch),'b',d.time,displaced(:,ch),'r',d.time,difference(:,ch),'k'); hold on;
        hs=plot(d.time(significant(:,ch)),difference(significant(:,ch),ch),'.','Color',[.7 .5 0]);
        if isempty(hs), hs=plot(NaN,NaN,'.','Color',[.7 .5 0]); end
        xline(0,'--m','HandleVisibility','off'); xline(.5,'--g','HandleVisibility','off'); title(d.channels{ch}); xlabel('Time from movement (s)'); ylabel('microvolts');
        if ch==1
            lg=legend([h;hs],{'Non-displaced','Displaced','Displaced - non-displaced','Bonferroni significant'});
            lg.Layout.Tile='south';
        end
    end
    sgtitle(sprintf('%s / %s (%s): non-displaced n=%d, displaced n=%d',cfg.subjects{s},session,cfg.analysisLabel,sum(labels==1),sum(labels==2)));
    stem=[cfg.subjects{s} '_' session '_averages'];
    exportgraphics(fig,fullfile(out,[stem '.png'])); close(fig);
    time=d.time; save(fullfile(out,[stem '.mat']),'correct','displaced','difference','p','significant','time','labels','trialMetadata','session','cfg');
  end
end
writetable(summary,fullfile(out,'session_counts.csv'));
