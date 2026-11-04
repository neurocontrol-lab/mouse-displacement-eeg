% Stage 4: session-level group averages with equal participant weights.
% Inputs: stage-3 participant/session means and contributor counts.
% Outputs: group PNG/MAT figures and explicit participant/trial counts.
% Paired tests use participant mean differences, with Bonferroni correction
% within each session. Eligibility requires two trials per condition.
% Session comparisons do not by themselves establish a stimulation effect.
pipelineDir=fileparts(mfilename('fullpath'));
codeDir=fileparts(pipelineDir);
addpath(codeDir,pipelineDir,fullfile(codeDir,'helpers'));
if ~exist('cfg','var') || ~isstruct(cfg) || ~isfield(cfg,'experimentId')
    cfg=config('PRE_06');
end
source=fullfile(cfg.output,'figures','by_session');
out=fullfile(cfg.output,'figures','group_sessions'); if ~isfolder(out), mkdir(out); end
counts=readtable(fullfile(source,'session_counts.csv'),'Delimiter',',','TextType','string');
groupSummary=table();
for ss=1:numel(cfg.sessions)
    session=cfg.sessions{ss}; C=[]; E=[]; subjects=strings(0,1); subjectCounts=table();
    for s=1:numel(cfg.subjects)
        row=counts(counts.subject==string(cfg.subjects{s}) & counts.session==string(session),:);
        if isempty(row) || row.nonDisplaced<2 || row.displaced<2, continue; end
        d=load(fullfile(source,[cfg.subjects{s} '_' session '_averages.mat']));
        if ~isempty(C), assert(isequal(time,d.time),'Time axes differ'); end
        time=d.time;
        C=cat(3,C,d.correct); E=cat(3,E,d.displaced);
        subjects(end+1,1)=string(cfg.subjects{s}); subjectCounts=[subjectCounts;row]; %#ok<AGROW>
    end
    N=numel(subjects); assert(N>=2,'Fewer than two eligible subjects for %s',session);
    correct=mean(C,3); displaced=mean(E,3); subjectDifference=E-C;
    difference=mean(subjectDifference,3); differenceSEM=std(subjectDifference,0,3)/sqrt(N);
    [~,p]=ttest(subjectDifference,0,'Dim',3); significant=p<cfg.alpha/numel(p);
    fig=figure('Visible','off','Position',[100 100 1100 1000]); tiledlayout(4,2);
    for ch=1:8
        nexttile; hold on;
        lo=difference(:,ch)-differenceSEM(:,ch); hi=difference(:,ch)+differenceSEM(:,ch);
        fill([time fliplr(time)],[lo' fliplr(hi')],[.85 .85 .85],'EdgeColor','none','HandleVisibility','off');
        h=plot(time,correct(:,ch),'b',time,displaced(:,ch),'r',time,difference(:,ch),'k');
        hs=plot(time(significant(:,ch)),difference(significant(:,ch),ch),'.','Color',[.7 .5 0]);
        xline(0,'--m','HandleVisibility','off'); xline(.5,'--g','HandleVisibility','off');
        title(cfg.channels{ch}); xlabel('Time from movement (s)'); ylabel('microvolts');
        if ch==1
            lg=legend([h;hs],{'Non-displaced','Displaced','Difference (shading: +/-1 SEM)','Paired Bonferroni significant'});
            lg.Layout.Tile='south';
        end
    end
    sgtitle(sprintf('All eligible subjects / %s: N=%d; equal subject weights',session,N));
    exportgraphics(fig,fullfile(out,[session '_group_average.png'])); close(fig);
    save(fullfile(out,[session '_group_average.mat']),'correct','displaced','difference',...
        'differenceSEM','C','E','subjectDifference','p','significant','subjects','subjectCounts','time','cfg');
    writetable(subjectCounts,fullfile(out,[session '_contributors.csv']));
    groupSummary=[groupSummary;table(string(session),N,sum(subjectCounts.nonDisplaced),sum(subjectCounts.displaced),...
        'VariableNames',{'session','subjects','nonDisplacedTrials','displacedTrials'})]; %#ok<AGROW>
    fprintf('Group %s: %d subjects\n',session,N);
end
writetable(groupSummary,fullfile(out,'group_counts.csv'));
