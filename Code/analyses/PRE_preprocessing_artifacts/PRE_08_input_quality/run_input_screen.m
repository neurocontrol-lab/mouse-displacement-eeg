% PRE_08: Input-quality screen.
% Workflow, execution order and interpretation: ../README.md#pre_08.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Input-only pilot: no FORCe, epoch low-pass, amplitude rejection or classification.
root = project_root();
addpath(fullfile(root,'Code'));
cfg=dataset_config();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_08_input_quality');
if ~isfolder(out)
    mkdir(out);
end
figdir=fullfile(out,'figures');
if ~isfolder(figdir)
    mkdir(figdir);
end
M=readtable(fullfile(cfg.parsedOutput,'manifest.csv'),'TextType','string');
M=M(ismember(M.subject,["mle01","spe30"]) & M.validTrials>0,:);
M=sortrows(M,{'subject','session','recordingDate','runNumber','run'});
writetable(M,fullfile(out,'selected_manifest.csv'));
fs=500;
[bh,ah]=butter(4,1/(fs/2),'high');
time=(-750:749)'/fs;
h=hann(500,'periodic');
freq=(0:250)';
powerScale=fs*sum(h.^2);
featureRows=cell(100000,22);
nr=0;
trialRows=cell(4000,14);
nt=0;
inventory=cell(height(M),7);
subjects=["mle01","spe30"];
sessions=["pre","post","retest"];
eventSum=zeros(1500,8,2,3,2);
eventN=zeros(2,3,2);
targetSum=zeros(301,8,2,3,2);
targetN=eventN;
for f=1:height(M)
    p=load(fullfile(cfg.parsedOutput,M.run(f)+'.mat'));
    raw=readmatrix(fullfile(root,'data',M.subject(f),M.run(f)+'.easy'),'FileType','text');
    eeg=raw(:,1:8)/1000;
    bad=raw(:,12)==255 | any(~isfinite(eeg),2);
    g=find(diff(raw(:,13))~=2);
    bad(g)=true;
    bad(g+1)=true;
    e=diff([false;~bad;false]);
    first=find(e==1);
    last=find(e==-1)-1;
    HP=nan(size(eeg));
    good=false(size(bad));
    for seg=1:numel(first)
        ix=first(seg):last(seg);
        if numel(ix)<=2000
            continue;
        end;
        HP(ix,:)=filtfilt(bh,ah,eeg(ix,:));
        good(first(seg)+1000:last(seg)-1000)=true;
    end
    eligible=0;
    invalid=0;
    guarded=0;
    bounds=0;
    s=find(subjects==M.subject(f));
    ss=find(sessions==M.session(f));
    for k=1:height(p.trials)
        if ~p.trials.valid(k)
            invalid=invalid+1;
            continue;
        end
        ix=p.trials.movementSample(k)+(-750:749);
        if min(ix)<1 || max(ix)>size(eeg,1)
            bounds=bounds+1;
            continue;
        end
        if ~all(good(ix))
            guarded=guarded+1;
            continue;
        end
        eligible=eligible+1;
        x=HP(ix,:);
        r=eeg(ix,:);
        nt=nt+1;
        targetRel=(p.trials.targetSample(k)-p.trials.movementSample(k))/fs;
        displaceRel=(p.trials.displacementSample(k)-p.trials.movementSample(k))/fs;
        trialRows(nt,:)={M.subject(f),M.session(f),M.runNumber(f),M.run(f),p.trials.trial(k),p.trials.label(k),k,f,targetRel,displaceRel,max(abs(x),[],'all'),max(max(x)-min(x)),max(max(r)-min(r)),true};
        lab=p.trials.label(k);
        base=time>=-.2 & time<0;
        xbase=x-mean(x(base,:),1);
        eventSum(:,:,s,ss,lab)=eventSum(:,:,s,ss,lab)+xbase;
        eventN(s,ss,lab)=eventN(s,ss,lab)+1;
        ti=p.trials.targetSample(k)+(-100:200);
        if min(ti)>=1 && max(ti)<=size(eeg,1) && all(good(ti))
            tx=HP(ti,:);
            tx=tx-mean(tx(51:100,:),1);
            targetSum(:,:,s,ss,lab)=targetSum(:,:,s,ss,lab)+tx;
            targetN(s,ss,lab)=targetN(s,ss,lab)+1;
        end
        for w=1:3
            wi=(w-1)*500+(1:500);
            z=x(wi,:);
            rz=r(wi,:);
            center=z-mean(z,1);
            ps=abs(fft(center.*h,500)).^2/powerScale;
            ps=ps(1:251,:);
            ps(2:end-1,:)=2*ps(2:end-1,:);
            low=sum(ps(freq>=1 & freq<=4,:),1);
            mid=sum(ps(freq>=8 & freq<=20,:),1);
            hf=sum(ps(freq>=30 & freq<=90 & ~(freq>=48 & freq<=52),:),1);
            line=sum(ps(freq>=49 & freq<=51,:),1);
            wide=sum(ps(freq>=1 & freq<=90,:),1);
            range=max(z)-min(z);
            rawrange=max(rz)-min(rz);
            [step,stepAt]=max(abs(diff(z)),[],1);
            [peak,peakAt]=max(abs(center),[],1);
            for ch=1:8
                nr=nr+1;
                featureRows(nr,:)={M.subject(f),M.session(f),M.runNumber(f),M.run(f),p.trials.trial(k),lab,w,-1.5+(w-1),-.5+(w-1),string(cfg.channels{ch}),max(abs(z(:,ch))),range(ch),sqrt(mean(center(:,ch).^2)),sqrt(low(ch)),sqrt(mid(ch)),sqrt(hf(ch)),line(ch)/max(wide(ch),eps),hf(ch)/max(wide(ch),eps),step(ch),time(wi(stepAt(ch)+1)),range(ch)/max(median(range),eps),rawrange(ch)};
            end
        end
    end
    inventory(f,:)={M.subject(f),M.session(f),M.runNumber(f),M.run(f),height(p.trials),eligible,invalid+guarded+bounds};
    fprintf('Input screen %d/%d %s: %d eligible\n',f,height(M),M.run(f),eligible);
end
F=cell2table(featureRows(1:nr,:),'VariableNames',{'subject','session','runNumber','run','trial','label','window','startSeconds','endSeconds','channel','peakAbsUV','rangeUV','rmsUV','lowRmsUV','midRmsUV','highRmsUV','lineFraction','highFraction','maxStepUV','maxStepTime','spatialRangeRatio','rawRangeUV'});
T=cell2table(trialRows(1:nt,:),'VariableNames',{'subject','session','runNumber','run','trial','label','trialRow','manifestRow','targetRelativeSeconds','displacementRelativeSeconds','inputPeakAbsUV','inputMaxRangeUV','rawMaxRangeUV','eligible'});
[G,~,~,~,~]=findgroups(F.subject,F.session,F.channel,F.window);
F.lowZ=zeros(height(F),1);
F.highZ=F.lowZ;
F.stepZ=F.lowZ;
for group=1:max(G)
    mask=G==group;
    for feature=["low","high","step"]
        if feature=="step"
            v=F.maxStepUV(mask);
        else
            v=F.(feature+"RmsUV")(mask);
        end
        q=log10(max(v,1e-12));
        m=median(q);
        mad0=median(abs(q-m));
        if mad0>1e-12
            z=.67448975*(q-m)/mad0;
        else
            z=zeros(size(q));
        end;
        F.(feature+"Z")(mask)=z;
    end
end
F.lowFrequencyFlag=F.lowZ>3.5;
F.highFrequencyFlag=F.highZ>3.5;
F.localAbruptFlag=F.stepZ>3.5 & F.spatialRangeRatio>=3;
F.amplitudeScreen=F.peakAbsUV>100;
F.lineDominant=F.lineFraction>.25;
F.responseWindowOverlap=F.startSeconds<.8 & F.endSeconds>.4;
F.largeStepInResponse=F.maxStepTime>=.4 & F.maxStepTime<.8;
writetable(F,fullfile(out,'window_channel_metrics.csv'));
writetable(T,fullfile(out,'trial_inventory.csv'));
I=cell2table(inventory,'VariableNames',{'subject','session','runNumber','run','trialRows','eligible','excluded'});
writetable(I,fullfile(out,'recording_inventory.csv'));
save(fullfile(out,'event_averages.mat'),'eventSum','eventN','targetSum','targetN','time','subjects','sessions','cfg');
set(groot,'defaultAxesFontSize',12,'defaultTextFontSize',12);
% All eligible trials, high-pass inputs only: these are not neural-source labels.
for s=1:2
    f=figure('Visible','off','Position',[10 10 1300 950]);
    tiledlayout(3,2);
    for ss=1:3
        for view=1:2
            nexttile;
            hold on;
            for lab=1:2
                if view==1
                    v=squeeze(eventSum(:,[2 3 6 7],s,ss,lab))/eventN(s,ss,lab);
                    tt=time;
                else
                    v=squeeze(targetSum(:,[2 3 6 7],s,ss,lab))/max(targetN(s,ss,lab),1);
                    tt=(-100:200)'/fs;
                end
                posterior=mean(v(:,1:2),2);
                central=mean(v(:,3:4),2);
                if lab==1
                    col=[.1 .3 .8];
                else
                    col=[.85 .2 .2];
                end;
                plot(tt,posterior,'Color',col,'LineStyle','-');
                plot(tt,central,'Color',col,'LineStyle','--');
            end
            xline(0,'k:','HandleVisibility','off');
            grid on;
            xlabel('Time from marker (s)');
            ylabel('High-pass input (microvolts)');
            if view==1
                ename="movement";
            else
                ename="target";
            end;
            title(subjects(s)+" / "+sessions(ss)+" / "+ename);
            if ss==1 && view==1
                legend('ND posterior','ND central','D posterior','D central','Location','best');
            end
        end
    end
    exportgraphics(f,fullfile(figdir,sprintf('event_context_%d.png',s)),'Resolution',180);
    close(f);
end
fprintf('INPUT SCREEN COMPLETE: %d trials, %d one-second windows, %d channel-window rows\n',nt,nt*3,nr);
