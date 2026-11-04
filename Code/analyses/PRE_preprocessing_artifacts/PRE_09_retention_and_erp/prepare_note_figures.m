% PRE_09: Retention and matched ERP comparison.
% Workflow, execution order and interpretation: ../README.md#pre_09.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Vector figures for the research note; saved matched means and final trial outputs only.
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','report');
figdir=fullfile(out,'figures');
if ~isfolder(figdir)
    mkdir(figdir);
end
A=load(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','matched_erp','matched_erp_means.mat'));
addpath(fullfile(root,'Code'));
cfg=dataset_config();
col=[.15 .15 .15;.85 .2 .2;.1 .6 .3;.1 .3 .85];
names=["1 BP no-FORCe","2 BP FORCe","3 Split no-FORCe","4 Split FORCe"];
waves=["Correct (ND)","Error (D)","Error - Correct"];
set(groot,'defaultAxesFontSize',8);
for s=1:2
    for ss=1:3
        Y=zeros(1000,8,3,4);
        N=squeeze(A.counts(s,ss,:));
        for c=1:4
            Y(:,:,1,c)=A.pool(:,:,1,c,s,ss)/N(1);
            Y(:,:,2,c)=A.pool(:,:,2,c,s,ss)/N(2);
            Y(:,:,3,c)=Y(:,:,2,c)-Y(:,:,1,c);
        end
        for group=1:2
            fig=figure('Visible','off','Units','inches','Position',[.2 .2 7 8.8]);
            axes(fig,'Position',[.05 .92 .9 .04],'Visible','off');
            hold on;
            for c=1:4
                if mod(c,2)
                    ls='--';
                else
                    ls='-';
                end;
                plot(NaN,NaN,'Color',col(c,:),'LineStyle',ls,'DisplayName',names(c));
            end;
            legend('show','Orientation','horizontal','NumColumns',2,'Location','north','FontSize',8,'Box','off');
            for r=1:4
                ch=(group-1)*4+r;
                for w=1:3
                    axes(fig,'Position',[.075+.32*(w-1) .71-.205*(r-1) .25 .15]);
                    hold on;
                    for c=1:4
                        if mod(c,2)
                            ls='--';
                        else
                            ls='-';
                        end;
                        plot(A.t,Y(:,ch,w,c),'Color',col(c,:),'LineStyle',ls,'LineWidth',.9);
                    end
                    if w<3
                        lim=max(abs(Y(:,ch,1:2,:)),[],'all');
                    else
                        lim=max(abs(Y(:,ch,3,:)),[],'all');
                    end;
                    ylim(1.1*[-max(1,lim) max(1,lim)]);
                    xlim([-1 1]);
                    xticks([-1 0 1]);
                    grid on;
                    xline(0,'k-');
                    xline(-.5,'Color',[.55 .55 .55],'LineStyle',':');
                    xline(.5,'Color',[.55 .55 .55],'LineStyle',':');
                    if w==1
                        ylabel(string(cfg.channels{ch})+" (\muV)");
                    end;
                    if r==1
                        title(waves(w),'Interpreter','none','FontSize',9);
                    end;
                    if r==4
                        xlabel('Time (s)');
                    end
                end;
            end
            drawnow;
            set(fig,'PaperUnits','inches','PaperPosition',[0 0 7 8.8],'PaperSize',[7 8.8]);
            print(fig,fullfile(figdir,sprintf('%s_%s_group%d.pdf',A.subjects(s),A.sessions(ss),group)),'-dpdf','-painters');
            close(fig);
        end
        fprintf('Research-note ERP figures %s %s\n',A.subjects(s),A.sessions(ss));
    end;
end
S=readtable(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','quality','residual_review_selection.csv'),'TextType','string');
selected=[2 3 10 4];
focus=[1 1 4 5];
centres=[-.7 -.7 .4 .5];
for q=1:4
    r=find(S.reviewID==selected(q));
    a=load(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis','processed',S.run(r)+'.mat'),'X','tc','trials','accepted','reason');
    k=find(a.trials.trial==S.trial(r));
    fig=figure('Visible','off','Units','inches','Position',[.2 .2 7 4.7]);
    for row=1:2
        ch=[focus(q) 7];
        ch=ch(row);
        for view=1:2
            axes(fig,'Position',[.085+.49*(view-1) .58-.46*(row-1) .39 .32]);
            hold on;
            for c=1:4
                y=squeeze(a.X(k,:,ch,c));
                if all(isfinite(y))
                    if mod(c,2)
                        ls='--';
                    else
                        ls='-';
                    end;
                    plot(a.tc,y,'Color',col(c,:),'LineStyle',ls,'DisplayName',names(c),'LineWidth',1);
                end;
            end
            xline(0,'k-','HandleVisibility','off');
            xline(-.5,'Color',[.5 .5 .5],'LineStyle',':','HandleVisibility','off');
            xline(.5,'Color',[.5 .5 .5],'LineStyle',':','HandleVisibility','off');
            grid on;
            ylabel(string(cfg.channels{ch})+" (\muV)");
            xlabel('Time (s)');
            if view==1
                xlim([-1 1]);
                title('Full analysis interval','FontSize',9);
            else
                xlim(centres(q)+[-.12 .12]);
                title('Detail','FontSize',9);
            end;
            if row==1&&view==1
                legend('show','FontSize',6,'Location','best');
            end
        end;
    end
    drawnow;
    set(fig,'PaperUnits','inches','PaperPosition',[0 0 7 4.7],'PaperSize',[7 4.7]);
    print(fig,fullfile(figdir,sprintf('priority_%d.pdf',q)),'-dpdf','-painters');
    close(fig);
end
fprintf('RESEARCH NOTE VECTOR FIGURES COMPLETE\n');
