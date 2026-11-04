% PRE_07: Boundary analysis.
% Workflow, execution order and interpretation: ../README.md#pre_07.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis');
M=readtable(fullfile(out,'selected_manifest.csv'),'TextType','string');
figdir=fullfile(out,'figures');
if ~isfolder(figdir)
    mkdir(figdir);
end
labels=["BP control","BP FORCe","Split control","Split FORCe","Split before LP"];
chanNames=["Cz","FCz","All-eight maximum"];
bounds=[-.5 0 .5];
P=table();
R=table();
Ret=table();
C=table();
E=table();
PC=cell(150000,15);
pr=0;
RC=cell(100000,13);
rr=0;
pool=cell(2,3,4);
counts=zeros(2,3,2);
subjects=["mle01","spe30"];
sessions=["pre","post","retest"];
for f=1:height(M)
    a=load(fullfile(out,'processed',M.run(f)+'.mat'));
    t=a.tc;
    common=all(a.accepted,2);
    ix=find(common);
    Ret=[Ret;table(M.subject(f),M.session(f),M.run(f),height(a.trials),sum(a.eligible),sum(a.accepted(:,1)),sum(a.accepted(:,2)),sum(a.accepted(:,3)),sum(a.accepted(:,4)),sum(common),'VariableNames',{'subject','session','run','trialRows','eligible','BP_control','BP_FORCe','Split_control','Split_FORCe','matchedAll'})];
    ordinary=true(999,1);
    dt=t(2:end)';
    for boundary=bounds
        ordinary=ordinary & abs(dt-boundary)>.05;
    end
    s=find(subjects==M.subject(f));
    ss=find(sessions==M.session(f));
    for k=ix'
        ref=squeeze(a.X(k,:,:,1));
        sc=quantile(ref,.95,1)-quantile(ref,.05,1);
        assert(all(sc>1e-10));
        values=cell(1,5);
        for v=1:4
            values{v}=squeeze(a.X(k,:,:,v));
        end
        values{5}=squeeze(a.preSplit(k,a.time>=-1 & a.time<1,:));
        values{5}=values{5}-mean(values{5}(t>=-.2 & t<0,:),1);
        for v=1:5
            x=values{v};
            d=abs(diff(x));
            for b=1:3
                z=find(abs(t-bounds(b))<1e-10);
                j=abs(x(z,:)-x(z-1,:));
                [~,mx]=max(j);
                chs=[6 7 mx];
                for c=1:3
                    ch=chs(c);
                    o=d(ordinary,ch);
                    pr=pr+1;
                    PC(pr,:)={M.subject(f),M.session(f),M.run(f),a.trials.trial(k),a.trials.label(k),k,v,chanNames(c),ch,bounds(b),j(ch),j(ch)/sc(ch),100*mean(o<j(ch)),j(ch)/quantile(o,.95),sc(ch)};
                end
            end
        end
        % Common-trial signal-change residuals, after identical crop and baseline.
        xr=squeeze(a.X(k,:,:,3));
        continuous=squeeze(a.continuousSplit(k,:,:));
        residuals={xr-continuous,squeeze(a.X(k,:,:,4))-xr,squeeze(a.X(k,:,:,2))-ref};
        windows={true(size(t)),t>=-1 & t<-.8 | t>=.8,t>=.2 & t<.9,abs(t+.5)<=.05,abs(t-.5)<=.05};
        winNames=["Full","Edges","Response","Join_minus","Join_plus"];
        for test=1:3
            for ch=[6 7]
                e=residuals{test}(:,ch);
                for w=1:5
                    q=abs(e(windows{w}));
                    rr=rr+1;
                    RC(rr,:)={M.subject(f),M.session(f),M.run(f),a.trials.trial(k),test,string(a.cfg.channels{ch}),winNames(w),median(q),quantile(q,.95),max(q),median(q)/sc(ch),quantile(q,.95)/sc(ch),max(q)/sc(ch)};
                end
            end
        end
        lab=a.trials.label(k);
        if ismember(lab,[1 2])
            counts(s,ss,lab)=counts(s,ss,lab)+1;
            for v=1:4
                if isempty(pool{s,ss,v})
                    pool{s,ss,v}=zeros(1000,2,2);
                end
                pool{s,ss,v}(:,:,lab)=pool{s,ss,v}(:,:,lab)+values{v}(:,[6 7]);
            end
        end
    end
    audited=find(any(isfinite(a.centring),[2 3]));
    for k=audited'
        for w=1:3
            for ch=[6 7]
                shift=a.centring(k,w,ch);
                rm=a.reconstruction(k,w,ch);
                C=[C;table(M.subject(f),M.session(f),M.run(f),a.trials.trial(k),w,string(a.cfg.channels{ch}),a.inputMeans(k,w,ch),shift,rm,sqrt(max(0,rm^2-shift^2)),'VariableNames',{'subject','session','run','trial','window','channel','inputMeanUV','reconstructionShiftUV','reconstructionRMSUV','nonconstantRMSUV'})];
            end
        end
    end
    fprintf('Summarised %d/%d %s common %d\n',f,height(M),M.run(f),numel(ix));
end
P=cell2table(PC(1:pr,:),'VariableNames',{'subject','session','run','trial','label','row','condition','channel','channelIndex','boundary','jumpUV','normalisedJump','percentile','excess95','scaleUV'});
R=cell2table(RC(1:rr,:),'VariableNames',{'subject','session','run','trial','test','channel','window','medianUV','p95UV','maxUV','medianNorm','p95Norm','maxNorm'});
writetable(P,fullfile(out,'boundary_trials.csv'));
writetable(R,fullfile(out,'residual_trials.csv'));
writetable(Ret,fullfile(out,'retention.csv'));
writetable(C,fullfile(out,'centring_audit.csv'));
% Summaries retain participant/session separation; pooled rows are explicitly descriptive.
B=table();
for subject=["Pooled",subjects]
    for channel=chanNames
        for boundary=bounds
            for v=1:5
                sel=P.condition==v & P.channel==channel & P.boundary==boundary;
                if subject~="Pooled"
                    sel=sel & P.subject==subject;
                end
                z=P(sel,:);
                B=[B;table(subject,channel,boundary,v,height(z),median(z.jumpUV),quantile(z.jumpUV,.95),max(z.jumpUV),median(z.normalisedJump),quantile(z.normalisedJump,.95),100*mean(z.percentile>=99),median(z.excess95),'VariableNames',{'subject','channel','boundary','condition','N','medianUV','p95UV','maxUV','medianNorm','p95Norm','above99Percent','medianExcess95'})];
            end
        end
    end
end
writetable(B,fullfile(out,'boundary_summary.csv'));
D=table();
pairs=[2 1;4 3;2 4];
for subject=["Pooled",subjects]
    for channel=["Cz","FCz"]
        for boundary=[-.5 .5]
            for pair=1:3
                a=P(P.condition==pairs(pair,1) & P.channel==channel & P.boundary==boundary,:);
                b=P(P.condition==pairs(pair,2) & P.channel==channel & P.boundary==boundary,:);
                if subject~="Pooled"
                    a=a(a.subject==subject,:);
                    b=b(b.subject==subject,:);
                end
                assert(isequal(a.run,b.run) && isequal(a.trial,b.trial));
                dj=a.jumpUV-b.jumpUV;
                dn=a.normalisedJump-b.normalisedJump;
                D=[D;table(subject,channel,boundary,pair,height(a),median(dj),quantile(dj,.05),quantile(dj,.95),median(dn),100*mean(dj>0),'VariableNames',{'subject','channel','boundary','contrast','N','medianDeltaUV','p05DeltaUV','p95DeltaUV','medianDeltaNorm','positivePercent'})];
            end;
        end;
    end;
end
writetable(D,fullfile(out,'paired_boundary_summary.csv'));

RS=table();
for subject=["Pooled",subjects]
    for test=1:3
        for channel=["Cz","FCz"]
            for window=["Full","Edges","Response","Join_minus","Join_plus"]
                sel=R.test==test & R.channel==channel & R.window==window;
                if subject~="Pooled"
                    sel=sel & R.subject==subject;
                end
                z=R(sel,:);
                RS=[RS;table(subject,test,channel,window,height(z),median(z.medianUV),median(z.p95UV),max(z.maxUV),median(z.medianNorm),median(z.p95Norm),quantile(z.p95Norm,.95),'VariableNames',{'subject','test','channel','window','N','medianOfMedianUV','medianOfP95UV','maxUV','medianOfMedianNorm','medianOfP95Norm','p95OfP95Norm'})];
            end;
        end;
    end
end;
writetable(RS,fullfile(out,'residual_summary.csv'));
set(groot,'defaultAxesFontSize',14,'defaultTextFontSize',14);
colors=[.25 .25 .25;.85 .2 .2;.1 .6 .3;.1 .3 .8;.5 .3 .7];
fig=figure('Visible','off','Position',[10 10 1200 780]);
tiledlayout(2,2);
for c=1:2
    for bi=[1 3]
        nexttile;
        hold on;
        for v=1:4
            z=P.normalisedJump(P.channel==chanNames(c) & P.boundary==bounds(bi) & P.condition==v);
            z=sort(z);
            stairs(100*z,(1:numel(z))/numel(z),'Color',colors(v,:),'LineWidth',1.5);
        end
        xlabel('Jump / reference voltage range (%)');
        ylabel('Fraction of matched trials');
        title(sprintf('%s / boundary %+.1f s',chanNames(c),bounds(bi)));
        grid on;
        set(gca,'XScale','log');
        legend(labels(1:4),'Location','southeast');
    end
end;
exportgraphics(fig,fullfile(figdir,'boundary_distributions.png'),'Resolution',160);
close(fig);
% Typical and upper-tail examples selected on original FORCe Cz jump at +0.5.
z=P(P.condition==2 & P.channel=="Cz" & P.boundary==.5,:);
[~,ord]=sort(z.normalisedJump);
selected=z(ord(round([.5 .95]*height(z))),:);
writetable(selected,fullfile(out,'selected_examples.csv'));
fig=figure('Visible','off','Position',[10 10 1200 900]);
tiledlayout(2,2);
exNames=["Median-ranked","95th-percentile-ranked"];
for j=1:2
    a=load(fullfile(out,'processed',selected.run(j)+'.mat'));
    k=selected.row(j);
    ch=6;
    for view=1:2
        nexttile;
        hold on;
        for v=1:4
            plot(a.tc,squeeze(a.X(k,:,ch,v)),'Color',colors(v,:),'LineWidth',1.2);
        end
        for boundary=[-.5 .5]
            xline(boundary,'k:','HandleVisibility','off');
        end
        if view==1
            xlim([-1 1]);
        else
            xlim([.4 .6]);
        end
        xlabel('Time from movement (s)');
        ylabel('Cz (microvolts)');
        title({sprintf('%s / %s / run %d / trial %d',selected.subject(j),selected.session(j),M.runNumber(find(M.run==selected.run(j),1)),selected.trial(j)),char(exNames(j))},'FontSize',13,'Interpreter','none');
        legend(labels(1:4),'Location','best');
        grid on;
    end
end;
exportgraphics(fig,fullfile(figdir,'representative_trials.png'),'Resolution',160);
close(fig);
fig=figure('Visible','off','Position',[10 10 1200 800]);
tiledlayout(2,2);
for j=1:2
    a=load(fullfile(out,'processed',selected.run(j)+'.mat'));
    k=selected.row(j);
    for ch=[6 7]
        ref=squeeze(a.X(k,:,ch,1));
        scale=quantile(ref,.95)-quantile(ref,.05);
        old=squeeze(a.X(k,:,ch,2))-ref;
        proposed=squeeze(a.X(k,:,ch,4))-squeeze(a.X(k,:,ch,3));
        nexttile;
        plot(a.tc,100*old/scale,'Color',colors(2,:),'LineWidth',1.3);
        hold on;
        plot(a.tc,100*proposed/scale,'Color',colors(4,:),'LineWidth',1.3);
        xline(-.5,'k:','HandleVisibility','off');
        xline(.5,'k:','HandleVisibility','off');
        grid on;
        xlabel('Time (s)');
        ylabel('Residual / reference range (%)');
        title(exNames(j)+" / "+string(a.cfg.channels{ch}));
        legend('BP FORCe minus BP control','Split FORCe minus split control','Location','best');
    end
end
exportgraphics(fig,fullfile(figdir,'actual_cleaning_residuals.png'),'Resolution',160);
close(fig);

% Filter-only median and upper quantile residual envelope over matched controls.
Q=[];
for f=1:height(M)
    a=load(fullfile(out,'processed',M.run(f)+'.mat'));
    ok=all(a.accepted,2);
    for k=find(ok)'
        ref=squeeze(a.X(k,:,:,1));
        sc=quantile(ref,.95)-quantile(ref,.05);
        e=squeeze(a.X(k,:,:,3))-squeeze(a.continuousSplit(k,:,:));
        Q=cat(3,Q,e(:,[6 7])./sc([6 7]));
    end
end
[bl,al]=butter(4,20/250,'low');
tf=(-750:749)'/500;
full=(-10000:9999)'/500;
synthetic=table();
fig=figure('Visible','off','Position',[10 10 1200 850]);
tiledlayout(2,2);
for ch=1:2
    nexttile;
    hold on;
    plot(t,100*median(abs(Q(:,ch,:)),3),'b','LineWidth',1.5);
    plot(t,100*quantile(abs(Q(:,ch,:)),.95,3),'r');
    xline(-1,'k:');
    xline(1,'k:');
    title(char(chanNames(ch)));
    xlabel('Time (s)');
    ylabel('Absolute residual / reference range (%)');
    legend('Median across trials','95th percentile across trials');
    grid on;
end
for boundary=[-.5 .5]
    nexttile;
    hold on;
    step=double(tf>=boundary);
    impulse=double(abs(tf-boundary)<1e-10);
    ys=filtfilt(bl,al,step);
    yi=filtfilt(bl,al,impulse);
    long=filtfilt(bl,al,double(full>=boundary));
    long=long(full>=-1.5 & full<1.5);
    plot(tf-boundary,ys,'b','LineWidth',1.5);
    plot(tf-boundary,yi,'r','LineWidth',1.5);
    plot(tf-boundary,ys-long,'k:');
    xlim([-.15 .15]);
    xlabel('Time from boundary (s)');
    ylabel('Residual / injected amplitude');
    title(sprintf('Response to injected disturbance at %+.1f s',boundary),'FontSize',12);
    legend('Persistent step','One-sample spike','Step: short minus long filtering');
    grid on;
    for j=1:numel(tf)
        synthetic=[synthetic;table(boundary,tf(j),ys(j),yi(j),ys(j)-long(j),'VariableNames',{'boundary','time','stepResponse','spikeResponse','shortMinusLong'})];
    end
end
exportgraphics(fig,fullfile(figdir,'filtering_effects.png'),'Resolution',160);
close(fig);
writetable(synthetic,fullfile(out,'synthetic_response.csv'));
save(fullfile(out,'residual_envelope.mat'),'Q','t');
% Condition difference waveforms and amplitude/peak-time descriptions.
response=t>=.2 & t<.9;
for s=1:2
    fig=figure('Visible','off','Position',[10 10 1200 850]);
    tiledlayout(3,2);
    for ss=1:3
        for ch=1:2
            nexttile;
            hold on;
            for v=1:4
                d=pool{s,ss,v}(:,ch,2)/counts(s,ss,2)-pool{s,ss,v}(:,ch,1)/counts(s,ss,1);
                plot(t,d,'Color',colors(v,:));
                ti=t(response);
                dd=d(response);
                [peak,at]=max(abs(dd));
                E=[E;table(subjects(s),sessions(ss),chanNames(ch),v,counts(s,ss,1),counts(s,ss,2),max(dd),min(dd),sqrt(mean(dd.^2)),peak,dd(at),ti(at),'VariableNames',{'subject','session','channel','condition','nonDisplaced','displaced','maxUV','minUV','rmsUV','absPeakUV','signedPeakUV','peakTimeSeconds'})];
            end
            xline(-.5,'k:','HandleVisibility','off');
            xline(.5,'k:','HandleVisibility','off');
            title(subjects(s)+" / "+sessions(ss)+" / "+chanNames(ch));
            xlabel('Time (s)');
            ylabel('D - ND (microvolts)');
            grid on;
            if s==1 && ss==1 && ch==1
                legend(labels(1:4));
            end
        end
    end
    exportgraphics(fig,fullfile(figdir,sprintf('erp_differences_%d.png',s)),'Resolution',160);
    close(fig);
end
writetable(E,fullfile(out,'erp_metrics.csv'));
disp(Ret);
disp(B(B.subject=="Pooled" & B.channel~="All-eight maximum",:));
disp(RS(RS.subject=="Pooled" & RS.window=="Response",:));
fprintf('ANALYSIS COMPLETE\n');
