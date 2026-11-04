% FEA_01: Feature audit and repeatability.
% Workflow, execution order and interpretation: ../README.md#fea_01.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Within-participant repeatability, raw samples and bins. Descriptive, no classifier.
root = project_root();
out=fullfile(root,'output','FEA_features_repeatability','FEA_01_feature_audit');
src=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis');
A=load(fullfile(out,'audit_data.mat'),'I','subjects','sessions','channels');
I=A.I;
M=readtable(fullfile(src,'selected_manifest.csv'),'TextType','string');
R=nan(height(I),350,8,4);
runMeans=nan(350,8,2,4,height(M));
runN=zeros(height(M),2);
t=(.2:.002:.898)';
for f=1:height(M)
    a=load(fullfile(src,'processed',M.run(f)+'.mat'),'X','trials','accepted');
    js=find(I.run==M.run(f));
    for j=js'
        k=find(a.trials.trial==I.trial(j));
        assert(isscalar(k)&&all(a.accepted(k,:)));
        R(j,:,:,:)=a.X(k,601:950,:,:);
    end
    for lab=1:2
        j=js(I.label(js)==lab);
        runN(f,lab)=numel(j);
        for c=1:4
            runMeans(:,:,lab,c,f)=squeeze(mean(R(j,:,:,c),1));
        end;
    end
end
assert(all(isfinite(R),'all'));
rows=cell(150000,20);
n=0;
halfCounts=cell(300,6);
hn=0;
rng(20261026,'twister');
for s=1:2
    for ss=1:3
        fs=find(M.subject==A.subjects(s)&M.session==A.sessions(ss));
        % Independent, class-count-matched halves stratified by run, same draws for all conditions.
        for rep=1:50
            na=[];
            da=[];
            nb=[];
            db=[];
            for f=fs'
                js=find(I.run==M.run(f));
                u=js(I.label(js)==1);
                v=js(I.label(js)==2);
                m=floor(min(numel(u),numel(v))/2);
                assert(m>=1);
                u=u(randperm(numel(u),2*m));
                v=v(randperm(numel(v),2*m));
                na=[na;u(1:m)];
                nb=[nb;u(m+1:2*m)];
                da=[da;v(1:m)];
                db=[db;v(m+1:2*m)];
            end
            assert(isempty(intersect([na;da],[nb;db])));
            hn=hn+1;
            halfCounts(hn,:)={A.subjects(s),A.sessions(ss),rep,numel(na),numel(da),numel(fs)};
            for c=1:4
                P=squeeze(mean(R(na,:,:,c),1));
                Q=squeeze(mean(R(da,:,:,c),1));
                U=squeeze(mean(R(nb,:,:,c),1));
                V=squeeze(mean(R(db,:,:,c),1));
                meta={A.subjects(s),A.sessions(ss),A.sessions(ss),c,"balanced_split_half",rep,"stratified_runs","stratified_runs",numel(na),numel(da),numel(nb),numel(db)};
                z=pairrows(P,Q,U,V,meta,A.channels,t);
                rows(n+(1:size(z,1)),:)=z;
                n=n+size(z,1);
            end
        end
        % Between distinct runs within the same session, using every common accepted trial.
        for i=1:numel(fs)-1
            for j=i+1:numel(fs)
                fa=fs(i);
                fb=fs(j);
                for c=1:4
                    meta={A.subjects(s),A.sessions(ss),A.sessions(ss),c,"between_runs",0,M.run(fa),M.run(fb),runN(fa,1),runN(fa,2),runN(fb,1),runN(fb,2)};
                    z=pairrows(runMeans(:,:,1,c,fa),runMeans(:,:,2,c,fa),runMeans(:,:,1,c,fb),runMeans(:,:,2,c,fb),meta,A.channels,t);
                    rows(n+(1:size(z,1)),:)=z;
                    n=n+size(z,1);
                end
            end;
        end
        fprintf('Repeatability %s %s: 50 balanced halves and %d run pairs\n',A.subjects(s),A.sessions(ss),nchoosek(numel(fs),2));
    end
    % Cross-session comparison is separate from within-session repeatability.
    for ss=1:2
        for tt=ss+1:3
            ia=find(I.subject==A.subjects(s)&I.session==A.sessions(ss));
            ib=find(I.subject==A.subjects(s)&I.session==A.sessions(tt));
            na=ia(I.label(ia)==1);
            da=ia(I.label(ia)==2);
            nb=ib(I.label(ib)==1);
            db=ib(I.label(ib)==2);
            for c=1:4
                meta={A.subjects(s),A.sessions(ss),A.sessions(tt),c,"between_sessions",0,A.sessions(ss),A.sessions(tt),numel(na),numel(da),numel(nb),numel(db)};
                z=pairrows(squeeze(mean(R(na,:,:,c),1)),squeeze(mean(R(da,:,:,c),1)),squeeze(mean(R(nb,:,:,c),1)),squeeze(mean(R(db,:,:,c),1)),meta,A.channels,t);
                rows(n+(1:size(z,1)),:)=z;
                n=n+size(z,1);
            end
        end;
    end
end
T=cell2table(rows(1:n,:),'VariableNames',{'subject','sessionA','sessionB','condition','test','replicate','recordingA','recordingB','nonDisplacedA','displacedA','nonDisplacedB','displacedB','resolution','waveform','channel','pearsonR','differenceRmsUV','normalisedDifferenceRms','responseMeanA','responseMeanB'});
writetable(T,fullfile(out,'repeatability_channel_metrics.csv'));
H=cell2table(halfCounts(1:hn,:),'VariableNames',{'subject','session','replicate','nonDisplacedPerHalf','displacedPerHalf','runs'});
writetable(H,fullfile(out,'repeatability_half_counts.csv'));
fprintf('REPEATABILITY COMPLETE: %d comparisons\n',height(T));
function C=pairrows(P,Q,U,V,meta,channels,t)
    AA={P,Q,(P+Q)/2,Q-P,P,Q};
    BB={U,V,(U+V)/2,V-U,V,U};
    waves=["ND","D","Shared","D_minus_ND","ND_to_D","D_to_ND"];
    C=cell(96,20);
    n=0;
    for res=1:2
        for w=1:6
            x=AA{w};
            y=BB{w};
            if res==2
                x=squeeze(mean(reshape(x,50,7,8),1));
                y=squeeze(mean(reshape(y,50,7,8),1));
                name="100ms";
                times=(.25:.1:.85)';
            else
                name="500Hz";
                times=t;
            end
            xc=x-mean(x,1);
            yc=y-mean(y,1);
            den=sqrt(sum(xc.^2,1).*sum(yc.^2,1));
            assert(all(den>1e-12));
            r=sum(xc.*yc,1)./den;
            e=sqrt(mean((x-y).^2,1));
            scale=sqrt((mean(x.^2,1)+mean(y.^2,1))/2);
            m=times>=.4&times<.8;
            ma=mean(x(m,:),1);
            mb=mean(y(m,:),1);
            for ch=1:8
                n=n+1;
                C(n,:)=[meta,{name,waves(w),channels(ch),r(ch),e(ch),e(ch)/scale(ch),ma(ch),mb(ch)}];
            end
        end;
    end
end
