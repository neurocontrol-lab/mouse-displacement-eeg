% FEA_01: Feature audit and repeatability.
% Workflow, execution order and interpretation: ../README.md#fea_01.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Repeatability figures: participant/session and channel-set separation retained.
root = project_root();
out=fullfile(root,'output','FEA_features_repeatability','FEA_01_feature_audit');
figdir=fullfile(out,'figures');
S=readtable(fullfile(out,'repeatability_summary.csv'),'TextType','string');
T=readtable(fullfile(out,'timepoint_summary.csv'),'TextType','string');
subjects=["mle01","spe30"];
sessions=["pre","post","retest"];
sets=["Central","Centroparietal","Posterior","Full"];
col=[.15 .15 .15;.85 .2 .2;.1 .6 .3;.1 .3 .85];
names=["1 BP no-FORCe","2 BP FORCe","3 Split no-FORCe","4 Split FORCe"];
waves=["ND","D","Shared","D_minus_ND","ND_to_D"];
set(groot,'defaultAxesFontSize',8);
for subject=subjects
    for test=["balanced_split_half","between_runs","between_sessions"]
        fig=figure('Visible','off','Units','inches','Position',[.2 .2 7 8.8]);
        axes(fig,'Position',[.05 .92 .9 .04],'Visible','off');
        hold on;
        for c=1:4
            plot(NaN,NaN,'o','Color',col(c,:),'DisplayName',names(c));
        end;
        legend('show','Orientation','horizontal','NumColumns',2,'Location','north','FontSize',8,'Box','off');
        for r=1:4
            for panel=1:3
                if test=="between_sessions"
                    p=[1 2;1 3;2 3];
                    sa=sessions(p(panel,1));
                    sb=sessions(p(panel,2));
                    ttl=sa+" vs "+sb;
                else
                    sa=sessions(panel);
                    sb=sa;
                    ttl=sa;
                end
                axes(fig,'Position',[.08+.32*(panel-1) .71-.205*(r-1) .25 .15]);
                hold on;
                for c=1:4
                    v=zeros(1,5);
                    low=v;
                    high=v;
                    for w=1:5
                        q=S(S.subject==subject&S.sessionA==sa&S.sessionB==sb&S.condition==c&S.test==test&S.resolution=="500Hz"&S.channelSet==sets(r)&S.waveform==waves(w),:);
                        assert(height(q)==1);
                        v(w)=q.pearsonRMedian;
                        low(w)=q.pearsonRP10;
                        high(w)=q.pearsonRP90;
                        if w==5
                            b=S(S.subject==subject&S.sessionA==sa&S.sessionB==sb&S.condition==c&S.test==test&S.resolution=="500Hz"&S.channelSet==sets(r)&S.waveform=="D_to_ND",:);
                            v(w)=mean([v(w) b.pearsonRMedian]);
                            low(w)=mean([low(w) b.pearsonRP10]);
                            high(w)=v(w);
                            low(w)=v(w);
                        end
                    end
                    x=(1:5)+(c-2.5)*.12;
                    errorbar(x,v,v-low,high-v,'o','Color',col(c,:),'MarkerSize',3,'LineWidth',.7,'CapSize',2);
                end
                xlim([.5 5.5]);
                ylim([-1 1]);
                yticks([-1 0 1]);
                xticks(1:5);
                xticklabels({'ND','D','S','D-ND','X'});
                grid on;
                yline(0,'k:');
                if panel==1
                    ylabel(sets(r)+": r");
                end;
                if r==1
                    title(ttl,'Interpreter','none','FontSize',9);
                end
            end;
        end
        drawnow;
        set(fig,'PaperUnits','inches','PaperPosition',[0 0 7 8.8],'PaperSize',[7 8.8]);
        file=fullfile(figdir,subject+"_"+test);
        print(fig,file,'-dpdf','-painters');
        print(fig,file,'-dpng','-r140');
        close(fig);
    end
end
% Direct illustration of cancellation in an original time-point class difference.
fig=figure('Visible','off','Units','inches','Position',[.2 .2 7 5.2]);
los=[.5 .7];
sss=["pre","post"];
for row=1:2
    lo=los(row);
    hi=lo+.1;
    ss=sss(row);
    q=T(T.subject=="spe30"&T.session==ss&T.channel=="FCz"&T.condition==1,:);
    x=q.timeSeconds;
    mask=x>=lo-1e-8&x<hi-1e-8;
    axes(fig,'Position',[.085 .58-.46*(row-1) .39 .30]);
    hold on;
    plot(x,q.meanND,'k-','DisplayName','ND: 500 Hz');
    plot(x,q.meanD,'Color',[.65 .1 .65],'DisplayName','D: 500 Hz');
    plot([lo hi],repmat(mean(q.meanND(mask)),1,2),'k--','HandleVisibility','off');
    plot([lo hi],repmat(mean(q.meanD(mask)),1,2),'--','Color',[.65 .1 .65],'HandleVisibility','off');
    xline(lo,'k:','HandleVisibility','off');
    xline(hi,'k:','HandleVisibility','off');
    xlim([lo-.1 hi+.1]);
    grid on;
    title("spe30 "+ss+": FCz, condition 1",'FontSize',9);
    ylabel('\muV');
    xlabel('Time (s)');
    if row==1
        legend('show','FontSize',7,'Location','best');
    end
    axes(fig,'Position',[.58 .58-.46*(row-1) .38 .30]);
    hold on;
    for c=1:4
        q=T(T.subject=="spe30"&T.session==ss&T.channel=="FCz"&T.condition==c,:);
        plot(q.timeSeconds,q.differenceUV,'Color',col(c,:),'DisplayName',names(c));
        m=q.timeSeconds>=lo-1e-8&q.timeSeconds<hi-1e-8;
        plot([lo hi],repmat(mean(q.differenceUV(m)),1,2),'--','Color',col(c,:),'HandleVisibility','off');
    end
    xline(lo,'k:','HandleVisibility','off');
    xline(hi,'k:','HandleVisibility','off');
    xlim([lo-.1 hi+.1]);
    grid on;
    title('D - ND; dashed segment = bin mean','FontSize',9);
    ylabel('\muV');
    xlabel('Time (s)');
    if row==1
        legend('show','FontSize',6,'Location','best');
    end
end
drawnow;
set(fig,'PaperUnits','inches','PaperPosition',[0 0 7 5.2],'PaperSize',[7 5.2]);
file=fullfile(figdir,'bin_cancellation_examples');
print(fig,file,'-dpdf','-painters');
print(fig,file,'-dpng','-r140');
close(fig);
fprintf('REPEATABILITY AND CANCELLATION FIGURES COMPLETE\n');
