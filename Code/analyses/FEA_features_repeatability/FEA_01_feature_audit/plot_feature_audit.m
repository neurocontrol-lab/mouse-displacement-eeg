% FEA_01: Feature audit and repeatability.
% Workflow, execution order and interpretation: ../README.md#fea_01.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Raw 500 Hz class means versus 100 ms features, identical trial IDs throughout.
root = project_root();
out=fullfile(root,'output','FEA_features_repeatability','FEA_01_feature_audit');
A=load(fullfile(out,'audit_data.mat'));
figdir=fullfile(out,'figures');
if ~isfolder(figdir)
    mkdir(figdir);
end
sets={ [6 7],[5 4],[1 2 3],1:8 };
setNames=["Central","Centroparietal","Posterior","Full montage"];
names=["1 BP no-FORCe","2 BP FORCe","3 Split no-FORCe","4 Split FORCe"];
col=[.15 .15 .15;.85 .2 .2;.1 .6 .3;.1 .3 .85];
waves=["Non-displaced (ND)","Displaced (D)","D minus ND"];
bc=(A.binStart+A.binEnd)/2;
mask=601:950;
reorder=[6 7 5 4 1 2 3 8];
Dtime=cell(2,3,4);
Dbin=Dtime;
globalMax=0;
for s=1:2
    for ss=1:3
        for c=1:4
            n1=A.N(s,ss,1);
            n2=A.N(s,ss,2);
            m1=A.sums(:,:,1,c,s,ss)/n1;
            m2=A.sums(:,:,2,c,s,ss)/n2;
            varianceND=max((A.squares(:,:,1,c,s,ss)-n1*m1.^2)/(n1-1),0);
            varianceD=max((A.squares(:,:,2,c,s,ss)-n2*m2.^2)/(n2-1),0);
            sp=sqrt(((n1-1)*varianceND+(n2-1)*varianceD)/(n1+n2-2));
            Dtime{s,ss,c}=(m2(mask,:)-m1(mask,:))./sp(mask,:);
            sel=A.I.subject==A.subjects(s)&A.I.session==A.sessions(ss);
            labels=A.I.label(sel);
            x=A.B(sel,:,c);
            p=x(labels==1,:);
            q=x(labels==2,:);
            pooled=sqrt(((n1-1)*var(p,0,1)+(n2-1)*var(q,0,1))/(n1+n2-2));
            z=(mean(q,1)-mean(p,1))./pooled;
            Dbin{s,ss,c}=reshape(z,7,8);
            globalMax=max([globalMax;abs(Dtime{s,ss,c}(:));abs(Dbin{s,ss,c}(:))]);
        end;
    end;
end
cl=ceil(globalMax*10)/10;
map=interp1([0 .5 1],[.15 .3 .8;1 1 1;.8 .15 .12],linspace(0,1,256));
set(groot,'defaultAxesFontSize',8);
for s=1:2
    for ss=1:3
        Y=zeros(1000,8,3,4);
        for c=1:4
            Y(:,:,1,c)=A.sums(:,:,1,c,s,ss)/A.N(s,ss,1);
            Y(:,:,2,c)=A.sums(:,:,2,c,s,ss)/A.N(s,ss,2);
            Y(:,:,3,c)=Y(:,:,2,c)-Y(:,:,1,c);
        end
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
            chs=sets{r};
            G=squeeze(mean(Y(:,chs,:,:),2));
            ce=max(abs(G(:,1:2,:)),[],'all');
            di=max(abs(G(:,3,:)),[],'all');
            for w=1:3
                axes(fig,'Position',[.08+.32*(w-1) .71-.205*(r-1) .25 .15]);
                hold on;
                for c=1:4
                    if mod(c,2)
                        ls='--';
                    else
                        ls='-';
                    end;
                    y=G(:,w,c);
                    plot(A.t(mask),y(mask),'Color',col(c,:),'LineStyle',ls,'LineWidth',.8);
                    b=zeros(7,1);
                    for j=1:7
                        ix=(round((A.binStart(j)+1)*500)+1):round((A.binEnd(j)+1)*500);
                        b(j)=mean(y(ix));
                    end;
                    plot(bc,b,'o','Color',col(c,:),'MarkerFaceColor','w','MarkerSize',3,'LineWidth',.8,'HandleVisibility','off');
                end
                xlim([.2 .9]);
                xticks([.2 .5 .9]);
                if w<3
                    lim=ce;
                else
                    lim=di;
                end;
                ylim(1.1*[-max(lim,1) max(lim,1)]);
                grid on;
                xline(.5,'Color',[.5 .5 .5],'LineStyle',':');
                yline(0,'Color',[.7 .7 .7]);
                if w==1
                    ylabel(setNames(r)+" (\muV)");
                end;
                if r==1
                    title(waves(w),'FontSize',9,'Interpreter','none');
                end;
                if r==4
                    xlabel('Seconds from movement');
                end
            end;
        end
        drawnow;
        set(fig,'PaperUnits','inches','PaperPosition',[0 0 7 8.8],'PaperSize',[7 8.8]);
        file=fullfile(figdir,A.subjects(s)+"_"+A.sessions(ss)+"_means");
        print(fig,file,'-dpdf','-painters');
        print(fig,file,'-dpng','-r140');
        close(fig);
        fig=figure('Visible','off','Units','inches','Position',[.2 .2 7 8.8]);
        colormap(fig,map);
        for c=1:4
            for resolution=1:2
                if resolution==1
                    pos=[.09 .735-.21*(c-1) .36 .145];
                    Z=Dtime{s,ss,c}(:,reorder)';
                    xx=A.t(mask);
                    titleText=names(c)+": 500 Hz";
                else
                    pos=[.57 .735-.21*(c-1) .30 .145];
                    Z=Dbin{s,ss,c}(:,reorder)';
                    xx=bc;
                    titleText="100 ms means";
                end
                axes(fig,'Position',pos);
                imagesc(xx,1:8,Z);
                clim([-cl cl]);
                yticks(1:8);
                yticklabels(A.channels(reorder));
                xticks([.2 .5 .9]);
                xlim([.2 .9]);
                title(titleText,'FontSize',8,'Interpreter','none');
                hold on;
                for boundary=[2.5 4.5 7.5]
                    yline(boundary,'Color',[.4 .4 .4],'LineWidth',.7);
                end;
                xline(.5,'k:');
                if c==4
                    xlabel('Seconds from movement');
                end
            end;
        end
        cb=colorbar('Position',[.925 .11 .018 .74]);
        ylabel(cb,'Signed Cohen d (D - ND)','FontSize',8);
        drawnow;
        set(fig,'PaperUnits','inches','PaperPosition',[0 0 7 8.8],'PaperSize',[7 8.8]);
        file=fullfile(figdir,A.subjects(s)+"_"+A.sessions(ss)+"_separation");
        print(fig,file,'-dpdf','-painters');
        print(fig,file,'-dpng','-r140');
        close(fig);
        fprintf('Feature audit plots %s %s\n',A.subjects(s),A.sessions(ss));
    end;
end
fprintf('FEATURE AUDIT FIGURES COMPLETE; shared d colour limit +/- %.1f\n',cl);
