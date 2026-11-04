% PRE_09: Retention and matched ERP comparison.
% Workflow, execution order and interpretation: ../README.md#pre_09.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Matched eight-channel Correct/Error/Error-Correct pilot from saved outputs.
% No FORCe or filtering is rerun; all four conditions share the same accepted trial IDs.
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','matched_erp');
src=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis');
addpath(fullfile(root,'Code'));
cfg=dataset_config();
figdir=fullfile(out,'figures');
if ~isfolder(figdir)
    mkdir(figdir);
end
M=readtable(fullfile(src,'selected_manifest.csv'),'TextType','string');
subjects=["mle01","spe30"];
sessions=["pre","post","retest"];
names=["BP no-FORCe","BP FORCe","Split no-FORCe","Split FORCe"];
colors=[.15 .15 .15;.85 .2 .2;.1 .6 .3;.1 .3 .85];
pool=zeros(1000,8,2,4,2,3);
counts=zeros(2,3,2);
own=zeros(2,3,2,4);
ids=cell(4000,8);
ni=0;
ret=cell(1000,9);
nr=0;
for f=1:height(M)
    a=load(fullfile(src,'processed',M.run(f)+'.mat'),'X','accepted','eligible','reason','trials','tc','names');
    assert(isequal(string(a.names),["BP_control","BP_FORCe","Split_control","Split_FORCe"]));
    t=a.tc(:);
    assert(numel(t)==1000 && abs(t(1)+1)<1e-12 && abs(t(end)-.998)<1e-12);
    s=find(subjects==M.subject(f));
    ss=find(sessions==M.session(f));
    common=all(a.accepted,2);
    assert(all(~common|a.eligible));
    for lab=1:2
        for c=1:4
            own(s,ss,lab,c)=own(s,ss,lab,c)+sum(a.accepted(:,c)&a.trials.label==lab);
        end
        ix=find(common & a.trials.label==lab);
        counts(s,ss,lab)=counts(s,ss,lab)+numel(ix);
        for k=ix'
            ni=ni+1;
            ids(ni,:)={M.subject(f),M.session(f),M.runNumber(f),M.run(f),a.trials.trial(k),lab,k,"accepted_all_four"};
            for c=1:4
                z=squeeze(a.X(k,:,:,c));
                assert(all(isfinite(z),'all'));
                assert(max(abs(mean(z(t>=-.2&t<0,:),1)))<1e-8);
                assert(max(abs(z),[],'all')<=100);
                pool(:,:,lab,c,s,ss)=pool(:,:,lab,c,s,ss)+z;
            end
        end
        nr=nr+1;
        ret(nr,:)={M.subject(f),M.session(f),M.run(f),lab,sum(a.eligible&a.trials.label==lab),sum(a.accepted(:,1)&a.trials.label==lab),sum(a.accepted(:,2)&a.trials.label==lab),sum(a.accepted(:,3)&a.trials.label==lab),sum(a.accepted(:,4)&a.trials.label==lab)};
    end
    fprintf('Matched ERP inputs %d/%d %s: %d common trials\n',f,height(M),M.run(f),sum(common));
end
I=cell2table(ids(1:ni,:),'VariableNames',{'subject','session','runNumber','run','trial','label','trialRow','selection'});
writetable(I,fullfile(out,'matched_trial_ids.csv'));
R=cell2table(ret(1:nr,:),'VariableNames',{'subject','session','run','label','eligible','BP_noFORCe','BP_FORCe','Split_noFORCe','Split_FORCe'});
writetable(R,fullfile(out,'retention_by_run_and_label.csv'));
metrics=cell(2000,16);
nm=0;
curves=cell(600000,9);
nc=0;
deltas=cell(2000,17);
nd=0;
waves=["Correct_ND","Error_D","Error_minus_Correct"];
winNames=["main_0.4_0.8","broad_0.2_0.9"];
windows={t>=.4&t<.8,t>=.2&t<.9};
pairs=[2 1;4 3;3 1;4 2];
for s=1:2
    for ss=1:3
        N=squeeze(counts(s,ss,:));
        assert(all(N>0));
        Y=zeros(1000,8,3,4);
        for c=1:4
            Y(:,:,1,c)=pool(:,:,1,c,s,ss)/N(1);
            Y(:,:,2,c)=pool(:,:,2,c,s,ss)/N(2);
            Y(:,:,3,c)=Y(:,:,2,c)-Y(:,:,1,c);
        end
        for ch=1:8
            for w=1:3
                for c=1:4
                    y=Y(:,ch,w,c);
                    for j=1:1000
                        nc=nc+1;
                        curves(nc,:)={subjects(s),sessions(ss),string(cfg.channels{ch}),c,waves(w),t(j),y(j),N(1),N(2)};
                    end
                    for wi=1:2
                        v=y(windows{wi});
                        tt=t(windows{wi});
                        [positive,pi]=max(v);
                        [negative,mi]=min(v);
                        [ap,ai]=max(abs(v));
                        nm=nm+1;
                        metrics(nm,:)={subjects(s),sessions(ss),string(cfg.channels{ch}),c,waves(w),winNames(wi),N(1),N(2),mean(v),sqrt(mean(v.^2)),positive,tt(pi),negative,tt(mi),v(ai),tt(ai)};
                    end
                end
                for pair=1:4
                    c=pairs(pair,1);
                    ref=pairs(pair,2);
                    for wi=1:2
                        mask=windows{wi};
                        v=Y(mask,ch,w,c);
                        b=Y(mask,ch,w,ref);
                        tt=t(mask);
                        [~,vi]=max(abs(v));
                        [~,bi]=max(abs(b));
                        [vp,vpi]=max(v);
                        [bp,bpi]=max(b);
                        [vm,vmi]=min(v);
                        [bm,bmi]=min(b);
                        e=v-b;
                        nd=nd+1;
                        deltas(nd,:)={subjects(s),sessions(ss),string(cfg.channels{ch}),c,ref,waves(w),winNames(wi),N(1),N(2),mean(e),sqrt(mean(e.^2)),max(abs(e)),v(vi)-b(bi),1000*(tt(vi)-tt(bi)),vp-bp,1000*(tt(vpi)-tt(bpi)),vm-bm};
                    end
                end
            end
        end
        fig=figure('Visible','off','Position',[20 20 1900 2700]);
        set(groot,'defaultAxesFontSize',10);
        annotation(fig,'textbox',[.03 .958 .94 .035],'String',{sprintf('%s / %s: matched eight-channel ERP comparison | Correct (ND) n=%d; Error (D) n=%d',subjects(s),sessions(ss),N(1),N(2));'Same trial IDs in all four conditions | movement marker 400 at 0 s | baseline [-0.2,0) s | joins at -0.5 and +0.5 s'},'EdgeColor','none','HorizontalAlignment','center','FontSize',12,'Interpreter','none');
        for ch=1:8
            ce=max(abs(Y(:,ch,1:2,:)),[],'all');
            di=max(abs(Y(:,ch,3,:)),[],'all');
            for w=1:3
                axes(fig,'Position',[.06+.32*(w-1) .84-.108*(ch-1) .275 .075]);
                hold on;
                for c=1:4
                    if mod(c,2)==0
                        ls='-';
                    else
                        ls='--';
                    end;
                    plot(t,Y(:,ch,w,c),'Color',colors(c,:),'LineStyle',ls,'LineWidth',1.15,'DisplayName',names(c));
                end
                xline(0,'k-','HandleVisibility','off');
                xline(-.5,'Color',[.5 .5 .5],'LineStyle',':','HandleVisibility','off');
                xline(.5,'Color',[.5 .5 .5],'LineStyle',':','HandleVisibility','off');
                yline(0,'Color',[.7 .7 .7],'HandleVisibility','off');
                xlim([-1 1]);
                if w<3
                    lim=ce;
                else
                    lim=di;
                end;
                ylim(1.12*[-max(lim,1) max(lim,1)]);
                grid on;
                xticks([-1 -.5 0 .5 1]);
                if w==1
                    ylabel(string(cfg.channels{ch})+" (microvolts)");
                else
                    ylabel('microvolts');
                end
                if ch==1
                    title(strrep(waves(w),'_',' '),'Interpreter','none');
                    if w==3
                        legend('show','Location','best','FontSize',8);
                    end;
                end
                if ch==8
                    xlabel('Seconds from movement');
                end
            end;
        end
        drawnow;
        set(fig,'PaperPositionMode','auto');
        print(fig,fullfile(figdir,subjects(s)+"_"+sessions(ss)+"_matched_erp.png"),'-dpng','-r140');
        close(fig);
        fprintf('ERP figures %s %s: ND=%d D=%d\n',subjects(s),sessions(ss),N(1),N(2));
    end;
end
C=cell2table(curves(1:nc,:),'VariableNames',{'subject','session','channel','condition','waveform','timeSeconds','meanUV','nonDisplaced','displaced'});
writetable(C,fullfile(out,'matched_waveforms.csv'));
E=cell2table(metrics(1:nm,:),'VariableNames',{'subject','session','channel','condition','waveform','window','nonDisplaced','displaced','meanUV','rmsUV','positivePeakUV','positivePeakTimeSeconds','negativePeakUV','negativePeakTimeSeconds','signedAbsPeakUV','absPeakTimeSeconds'});
writetable(E,fullfile(out,'response_metrics.csv'));
D=cell2table(deltas(1:nd,:),'VariableNames',{'subject','session','channel','condition','referenceCondition','waveform','window','nonDisplaced','displaced','deltaMeanUV','waveformDifferenceRmsUV','waveformDifferenceMaxUV','deltaSignedAbsPeakUV','deltaAbsPeakTimeMs','deltaPositivePeakUV','deltaPositivePeakTimeMs','deltaNegativePeakUV'});
writetable(D,fullfile(out,'paired_response_changes.csv'));
save(fullfile(out,'matched_erp_means.mat'),'Y','pool','counts','own','t','subjects','sessions','names');
fprintf('MATCHED EIGHT-CHANNEL ERP COMPLETE: %d common trials; %d metrics\n',ni,nm);
