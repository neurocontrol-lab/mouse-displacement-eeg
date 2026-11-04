% PRE_08: Input-quality screen.
% Workflow, execution order and interpretation: README.md in this folder.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_08_input_quality');
addpath(fullfile(root,'Code'));
cfg=dataset_config();
M=readtable(fullfile(out,'selected_manifest.csv'),'TextType','string');
S=readtable(fullfile(out,'review_selection.csv'),'TextType','string');
T=readtable(fullfile(out,'trial_screen_and_review.csv'),'TextType','string');
F=readtable(fullfile(out,'window_channel_metrics.csv'),'TextType','string');
B=readtable(fullfile(out,'screen_summary.csv'),'TextType','string');
figdir=fullfile(out,'figures');
[bh,ah]=butter(4,1/250,'high');
tt=(-750:749)'/500;
h=hann(500,'periodic');
fr=(0:250)';
set(groot,'defaultAxesFontSize',12,'defaultTextFontSize',12);
col=lines(8);
boundsum=zeros(1500,8,2,3,2);
boundn=zeros(2,3,2);
targetB=zeros(301,8,2,3,2);
targetBn=boundn;
subjects=["mle01","spe30"];
sessions=["pre","post","retest"];
S=S(S.reviewID==35,:);
M=M(M.run==S.run(1),:);
for f=1:height(M)
    p=load(fullfile(cfg.parsedOutput,M.run(f)+'.mat'));
    raw=readmatrix(fullfile(root,'data',M.subject(f),M.run(f)+'.easy'),'FileType','text');
    eeg=raw(:,1:8)/1000;
    bad=raw(:,12)==255 | any(~isfinite(eeg),2);
    g=find(diff(raw(:,13))~=2);
    bad(g)=true;
    bad(g+1)=true;
    d=diff([false;~bad;false]);
    first=find(d==1);
    last=find(d==-1)-1;
    HP=nan(size(eeg));
    good=false(size(bad));
    for j=1:numel(first)
        ix=first(j):last(j);
        if numel(ix)>2000
            HP(ix,:)=filtfilt(bh,ah,eeg(ix,:));
            good(first(j)+1000:last(j)-1000)=true;
        end;
    end
    s=find(subjects==M.subject(f));
    ss=find(sessions==M.session(f));
    rows=find(T.run==M.run(f) & T.inputPeakAbsUV<=100);
    for q=rows'
        k=T.trialRow(q);
        ix=p.trials.movementSample(k)+(-750:749);
        z=HP(ix,:);
        lab=T.label(q);
        z=z-mean(z(tt>=-.2 & tt<0,:),1);
        boundsum(:,:,s,ss,lab)=boundsum(:,:,s,ss,lab)+z;
        boundn(s,ss,lab)=boundn(s,ss,lab)+1;
        ti=p.trials.targetSample(k)+(-100:200);
        if min(ti)>=1 && max(ti)<=size(eeg,1) && all(good(ti))
            x=HP(ti,:);
            x=x-mean(x(51:100,:),1);
            targetB(:,:,s,ss,lab)=targetB(:,:,s,ss,lab)+x;
            targetBn(s,ss,lab)=targetBn(s,ss,lab)+1;
        end
    end
    for q=find(S.run==M.run(f))'
        k=S.trialRow(q);
        ix=p.trials.movementSample(k)+(-750:749);
        z=HP(ix,:);
        r=eeg(ix,:);
        fig=figure('Visible','off','Position',[10 10 1350 1100]);
        tiledlayout(3,1,'TileSpacing','compact');
        for view=1:2
            nexttile;
            hold on;
            if view==1
                x=z;
                name='Continuous 1 Hz high-pass input x';
            else
                x=r;
                name='Raw context (channel medians removed for display)';
            end
            x=x-median(x,1);
            spacing=max(20,1.1*max(max(x)-min(x)));
            for ch=1:8
                plot(tt,x(:,ch)+(8-ch)*spacing,'Color',col(ch,:));
            end
            yticks((0:7)*spacing);
            yticklabels(fliplr(cfg.channels));
            xlabel('Time from movement marker (s)');
            ylabel(sprintf('Channels; spacing %.1f microvolts',spacing));
            title(name);
            xline(0,'k:','HandleVisibility','off');
            xline(S.targetRelativeSeconds(q),'Color',[.8 .5 0],'LineStyle','--','HandleVisibility','off');
            if isfinite(S.displacementRelativeSeconds(q))
                xline(S.displacementRelativeSeconds(q),'Color',[0 .5 0],'LineStyle','--','HandleVisibility','off');
            end;
            grid on;
            xlim([-1.5 1.5]);
        end
        nexttile;
        hold on;
        ps=zeros(251,8);
        for w=1:3
            x=z((w-1)*500+(1:500),:);
            x=x-mean(x,1);
            pw=abs(fft(x.*h,500)).^2/(500*sum(h.^2));
            pw=pw(1:251,:);
            pw(2:end-1,:)=pw(2:end-1,:)*2;
            ps=ps+pw/3;
        end
        for ch=1:8
            semilogy(fr(2:151),max(ps(2:151,ch),1e-12),'Color',col(ch,:));
        end;
        set(gca,'YScale','log');
        xlabel('Frequency (Hz)');
        ylabel('Power density (microvolts squared / Hz)');
        title('Average of three one-second Hann periodograms; no FORCe');
        legend(cfg.channels,'Location','eastoutside');
        grid on;
        xlim([1 150]);
        sgtitle(sprintf('Review %02d: %s / %s / run %d / trial %d / label %d',S.reviewID(q),S.subject(q),S.session(q),S.runNumber(q),S.trial(q),S.label(q)),'Interpreter','none');
        exportgraphics(fig,fullfile(figdir,S.figure(q)),'Resolution',160);
        close(fig);
    end
    fprintf('Review figures %d/%d\n',f,height(M));
end

R=B(isfinite(B.runNumber),:);
fields=["lowFrequencyFlagTrials","highFrequencyFlagTrials","localAbruptFlagTrials","lineDominantTrials","grossExcursionTrials"];
values=zeros(height(R),5);
names=strings(height(R),1);
for j=1:height(R)
    for k=1:5
        values(j,k)=100*R.(fields(k))(j)/R.eligibleTrials(j);
    end;
    names(j)=sprintf('%s %s %s',R.subject(j),R.session(j),string(R.runNumber(j)));
end
fig=figure('Visible','off','Position',[10 10 1000 1250]);
imagesc(values);
colorbar;
clim([0 100]);
yticks(1:height(R));
yticklabels(names);
xticks(1:5);
xticklabels({'Slow outlier','HF outlier','Local abrupt','50 Hz fraction','>1 mV input'});
xtickangle(20);
title('Trials flagged per run (%); screen flags, not source labels');
for j=1:height(R)
    for k=1:5
        text(k,j,sprintf('%.1f',values(j,k)),'HorizontalAlignment','center','Color','w','FontSize',10);
    end;
end;
exportgraphics(fig,fullfile(figdir,'run_screen_rates.png'),'Resolution',160);
close(fig);
fprintf('INPUT REVIEW FIGURES COMPLETE\n');
