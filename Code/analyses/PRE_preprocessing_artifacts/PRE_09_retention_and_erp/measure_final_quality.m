% PRE_09: Retention and matched ERP comparison.
% Workflow, execution order and interpretation: ../README.md#pre_09.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Final-output quality screen using identical two-second measurements in all conditions.
% This reads saved outputs. FORCe is never rerun. Condition 0 is HP-only input context.
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','quality');
src=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis');
addpath(fullfile(root,'Code'));
cfg=dataset_config();
M=readtable(fullfile(src,'selected_manifest.csv'),'TextType','string');
[bh,ah]=butter(4,1/250,'high');
h=hann(1000,'periodic');
freq=(0:500)'*.5;
rows=cell(120000,23);
n=0;
for f=1:height(M)
    a=load(fullfile(src,'processed',M.run(f)+'.mat'),'X','accepted','reason','trials','tc','eligible');
    t=a.tc(:);
    response=t>=.4&t<.8;
    base=t>=-.2&t<0;
    raw=readmatrix(fullfile(root,'data',M.subject(f),M.run(f)+'.easy'),'FileType','text');
    eeg=raw(:,1:8)/1000;
    bad=raw(:,12)==255|any(~isfinite(eeg),2);
    g=find(diff(raw(:,13))~=2);
    bad(g)=true;
    bad(g+1)=true;
    d=diff([false;~bad;false]);
    first=find(d==1);
    last=find(d==-1)-1;
    hp=nan(size(eeg));
    for j=1:numel(first)
        ix=first(j):last(j);
        if numel(ix)>2000
            hp(ix,:)=filtfilt(bh,ah,eeg(ix,:));
        end;
    end
    for k=find(a.eligible)'
        ix=a.trials.movementSample(k)+(-500:499);
        input=hp(ix,:);
        input=input-mean(input(base,:),1);
        for c=0:4
            if c==0
                z=input;
                accepted=false;
            else
                z=squeeze(a.X(k,:,:,c));
                accepted=a.accepted(k,c);
            end
            if any(~isfinite(z),'all')
                continue;
            end
            x=z-mean(z,1);
            pw=abs(fft(x.*h,1000)).^2/(500*sum(h.^2));
            pw=pw(1:501,:);
            pw(2:end-1,:)=2*pw(2:end-1,:);
            lf=sqrt(sum(pw(freq>=1&freq<=4,:),1)*.5);
            hf=sqrt(sum(pw(freq>=30&freq<=90&~(freq>=48&freq<=52),:),1)*.5);
            range=max(z)-min(z);
            steps=abs(diff(z));
            dt=t(2:end);
            ordinary=abs(dt+.5)>.05&abs(dt-.5)>.05&abs(dt)>.05;
            for ch=1:8
                [st,si]=max(steps(:,ch));
                b=zeros(1,3);
                for bi=1:3
                    bt=[-.5 0 .5];
                    q=find(abs(t-bt(bi))<1e-9);
                    b(bi)=abs(z(q,ch)-z(q-1,ch));
                end
                n=n+1;
                rows(n,:)={M.subject(f),M.session(f),M.runNumber(f),M.run(f),a.trials.trial(k),a.trials.label(k),c,string(cfg.channels{ch}),accepted,lf(ch),hf(ch),range(ch),range(ch)/median(range),max(abs(z(:,ch))),max(abs(z(response,ch))),st,dt(si),quantile(steps(ordinary,ch),.95),b(1),b(2),b(3),max(abs(z(abs(t+.5)<=.05|abs(t-.5)<=.05,ch))),sqrt(mean(z(:,ch).^2))};
            end;
        end;
    end
    fprintf('Final quality metrics %d/%d %s\n',f,height(M),M.run(f));
end
Q=cell2table(rows(1:n,:),'VariableNames',{'subject','session','runNumber','run','trial','label','condition','channel','accepted','lowRmsUV','highRmsUV','rangeUV','spatialRangeRatio','peakAbsUV','responsePeakAbsUV','maxStepUV','maxStepTime','ordinaryStepP95UV','joinMinusStepUV','onsetStepUV','joinPlusStepUV','joinRegionPeakUV','rmsUV'});
writetable(Q,fullfile(out,'final_channel_metrics.csv'));
fprintf('FINAL QUALITY METRICS COMPLETE: %d channel/condition rows\n',height(Q));
