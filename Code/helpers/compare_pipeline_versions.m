% Compare the configured reference and current pipeline on matched trials.
% Dashed = reference; solid = current. Onset steps use samples -2 ms and 0 ms.
codeDir=fileparts(fileparts(mfilename('fullpath'))); addpath(codeDir,fullfile(codeDir,'original_pipeline')); cfg=config('PRE_06');
out=fullfile(cfg.output,'comparison'); if ~isfolder(out), mkdir(out); end
manifest=readtable(fullfile(cfg.output,'selected_manifest.csv'),'TextType','string');
summary=table(); steps=table(); waveforms=table();
for subject=string(cfg.subjects)
    for session=string(cfg.sessions)
        rows=find(manifest.subject==subject & manifest.session==session);
        oldX=[]; newX=[]; labels=[]; oldKeep=[]; newKeep=[]; meta=table();
        for row=rows'
            name=manifest.run(row)+".mat";
            d=load(fullfile(cfg.output,'processed',name));
            old=load(fullfile(cfg.comparisonOutput,'processed',name));
            assert(isequaln(old.trials.label,d.trials.label) && ...
                isequaln(old.trials.movementSample,d.trials.movementSample));
            assert(isequal(old.time,d.time) && isequal(old.channels,d.channels),'Axes differ');
            meta=[meta;d.trials(:,{'subject','session','recordingDate','runNumber','trial','label'})];
            oldX=cat(1,oldX,old.epochs); newX=cat(1,newX,d.epochs);
            labels=[labels;d.trials.label]; oldKeep=[oldKeep;old.trials.accepted];
            newKeep=[newKeep;d.trials.accepted];
        end
        if isempty(rows), continue; end
        common=oldKeep & newKeep;
        onset=find(d.time==0,1);
        referenceStep=max(abs(oldX(:,onset,:)-oldX(:,onset-1,:)),[],3);
        currentStep=max(abs(newX(:,onset,:)-newX(:,onset-1,:)),[],3);
        near=find(d.time>=-0.05 & d.time<=0.05); near(near==onset)=[];
        referenceNearby=median(max(abs(oldX(:,near,:)-oldX(:,near-1,:)),[],3),2);
        currentNearby=median(max(abs(newX(:,near,:)-newX(:,near-1,:)),[],3),2);
        meta.referenceAccepted=oldKeep; meta.currentAccepted=newKeep;
        meta.referenceStep=referenceStep; meta.currentStep=currentStep;
        meta.referenceNearby=referenceNearby; meta.currentNearby=currentNearby;
        steps=[steps;meta];
        for condition=1:2
            a=labels==condition;
            summary=[summary;table(subject,session,condition, ...
                sum(a & oldKeep),sum(a & newKeep),sum(a & common), ...
                sum(a & ~oldKeep & newKeep),sum(a & oldKeep & ~newKeep), ...
                median(referenceStep(a & common)),median(currentStep(a & common)), ...
                sum(currentStep(a & common)<referenceStep(a & common)), ...
                'VariableNames',{'subject','session','condition','referenceAccepted', ...
                'currentAccepted','common','recovered','lost','medianStepReference', ...
                'medianStepCurrent','smallerStep'})];
        end
        for mode=["common","own","onset"]
            if mode~="own", ka=common; kb=common; else, ka=oldKeep; kb=newKeep; end
            fig=figure('Visible','off','Position',[50 50 1150 1000]); tiledlayout(4,2);
            for ch=1:8
                nexttile; hold on;
                a=squeeze(mean(oldX(ka & labels==1,:,ch),1));
                b=squeeze(mean(newX(kb & labels==1,:,ch),1));
                e=squeeze(mean(oldX(ka & labels==2,:,ch),1));
                f=squeeze(mean(newX(kb & labels==2,:,ch),1));
                h=plot(d.time,a,'b--',d.time,b,'b-',d.time,e,'r--',d.time,f,'r-');
                xline(0,'k:','HandleVisibility','off'); title(d.channels{ch});
                xlabel('Time from movement (s)'); ylabel('microvolts');
                if mode=="onset", xlim([-0.1 0.1]); end
                if mode=="common"
                    post=d.time>=0.2 & d.time<1;
                    for condition=1:2
                        if condition==1, ref=a; cur=b; else, ref=e; cur=f; end
                        correlation=corr(ref(post)',cur(post)');
                        rmsDifference=sqrt(mean((cur(post)-ref(post)).^2));
                        waveforms=[waveforms;table(subject,session,condition,string(d.channels{ch}), ...
                            correlation,rmsDifference,'VariableNames', ...
                            {'subject','session','condition','channel','correlation','rmsDifferenceUV'})];
                    end
                end
                if ch==1
                    lg=legend(h,{[cfg.comparisonLabel ' non-displaced'],[cfg.analysisLabel ' non-displaced'], ...
                        [cfg.comparisonLabel ' displaced'],[cfg.analysisLabel ' displaced']});
                    lg.Layout.Tile='south';
                end
            end
            sgtitle(sprintf('%s / %s / %s: %s n=%d, %s n=%d', ...
                subject,session,mode,cfg.comparisonLabel,sum(ka),cfg.analysisLabel,sum(kb)));
            exportgraphics(fig,fullfile(out,subject+"_"+session+"_"+mode+".png")); close(fig);
        end

    end
end
writetable(summary,fullfile(out,'comparison_counts.csv'));
writetable(steps,fullfile(out,'onset_steps.csv'));
writetable(waveforms,fullfile(out,'waveform_comparison.csv'));
disp(summary);
