% PRE_09: Retention and matched ERP comparison.
% Workflow, execution order and interpretation: ../README.md#pre_09.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Inspect retained input flags against saved final signals; FORCe is not rerun.
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','quality');
addpath(fullfile(root,'Code'));
cfg=dataset_config();
S=readtable(fullfile(out,'review_selection.csv'),'TextType','string');
F=readtable(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_08_input_quality','window_channel_metrics.csv'),'TextType','string');
figdir=fullfile(out,'figures');
if ~isfolder(figdir)
    mkdir(figdir);
end
[bh,ah]=butter(4,1/250,'high');
tt=(-750:749)'/500;
colors=[.1 .1 .1;.85 .2 .2;.1 .6 .3;.15 .3 .9];
names=["BP no-FORCe","BP FORCe","Split no-FORCe","Split FORCe"];
set(groot,'defaultAxesFontSize',11,'defaultTextFontSize',11);
for q=1:height(S)
    a=load(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis','processed',S.run(q)+'.mat'),'X','accepted','reason','trials','tc');
    k=find(a.trials.trial==S.trial(q));
    assert(isscalar(k));
    raw=readmatrix(fullfile(root,'data',S.subject(q),S.run(q)+'.easy'),'FileType','text');
    eeg=raw(:,1:8)/1000;
    bad=raw(:,12)==255|any(~isfinite(eeg),2);
    g=find(diff(raw(:,13))~=2);
    bad(g)=true;
    bad(g+1)=true;
    d=diff([false;~bad;false]);
    first=find(d==1);
    last=find(d==-1)-1;
    ix=a.trials.movementSample(k)+(-750:749);
    j=find(first<=ix(1) & last>=ix(end));
    assert(isscalar(j));
    hp=filtfilt(bh,ah,eeg(first(j):last(j),:));
    x=hp(ix-first(j)+1,:);
    fig=figure('Visible','off','Position',[20 20 1400 1500]);
    tiledlayout(5,2,'TileSpacing','compact','Padding','compact');
    nexttile([1 2]);
    hold on;
    spacing=max(20,1.1*max(max(x)-min(x)));
    z=x-median(x,1);
    for ch=1:8
        plot(tt,z(:,ch)+(8-ch)*spacing);
    end;
    yticks((0:7)*spacing);
    yticklabels(fliplr(cfg.channels));
    xlim([-1.5 1.5]);
    grid on;
    xline(0,'k:');
    xline(-.5,'k--');
    xline(.5,'k--');
    title(sprintf('Input: continuous 1 Hz HP; full 3 s; channel spacing %.1f microvolts',spacing));
    xlabel('Seconds from movement');
    status=strings(1,4);
    for c=1:4
        if a.accepted(k,c)
            v="accepted";
        else
            v="rejected: "+a.reason(k,c);
        end;
        status(c)=names(c)+" ("+v+")";
    end
    for ch=1:8
        nexttile;
        hold on;
        for c=1:4
            y=squeeze(a.X(k,:,ch,c));
            if any(isfinite(y))
                if mod(c,2)==0
                    ls='-';
                else
                    ls='--';
                end;
                plot(a.tc,y,'Color',colors(c,:),'LineStyle',ls,'LineWidth',1.1,'DisplayName',names(c));
            end;
        end
        xline(0,'k:','HandleVisibility','off');
        xline(-.5,'Color',[.5 .5 .5],'LineStyle',':','HandleVisibility','off');
        xline(.5,'Color',[.5 .5 .5],'LineStyle',':','HandleVisibility','off');
        xlim([-1 1]);
        grid on;
        title(cfg.channels{ch});
        ylabel('microvolts');
        xlabel('Seconds from movement');
        if ch==1
            legend('show','Location','best','FontSize',8);
        end
    end
    sgtitle({sprintf('Review %d: %s / %s / run %d / trial %d / %s',S.reviewID(q),S.subject(q),S.session(q),S.runNumber(q),S.trial(q),S.trialClass(q));strjoin(status,' | ')},'Interpreter','none','FontSize',11);
    set(fig,'PaperPositionMode','auto');
    print(fig,fullfile(figdir,S.figure(q)),'-dpng','-r140');
    close(fig);
    f=F(F.run==S.run(q)&F.trial==S.trial(q),:);
    writetable(f,fullfile(figdir,sprintf('review_%02d_input_windows.csv',S.reviewID(q))));
    fprintf('Reviewed %d/%d %s trial %d\n',q,height(S),S.run(q),S.trial(q));
end
