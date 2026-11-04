% FEA_01: Feature audit and repeatability.
% Workflow, execution order and interpretation: README.md in this folder.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Audit exact matched trials at original sample resolution and 100 ms bin resolution.
% Existing outputs only; no cleaning/filtering is rerun.
root = project_root();
out=fullfile(root,'output','FEA_features_repeatability','FEA_01_feature_audit');
src=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis');
addpath(fullfile(root,'Code'));
cfg=dataset_config();
I=readtable(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','matched_erp','matched_trial_ids.csv'),'TextType','string');
M=readtable(fullfile(src,'selected_manifest.csv'),'TextType','string');
subjects=["mle01","spe30"];
sessions=["pre","post","retest"];
channels=string(cfg.channels);
% B: matched trials × 56 binned features (7 per channel) × 4 conditions.
B=nan(height(I),56,4);
% Accumulators: time × channel × ND/D × condition × participant × session.
sums=zeros(1000,8,2,4,2,3);
squares=sums;
N=zeros(2,3,2);
seen=false(height(I),1);
binStart=.2+(0:6)/10;
binEnd=binStart+.1;
for f=1:height(M)
    a=load(fullfile(src,'processed',M.run(f)+'.mat'),'X','tc','trials','accepted');
    t=a.tc(:);
    s=find(subjects==M.subject(f));
    ss=find(sessions==M.session(f));
    assert(isequal(t,(-500:499)'/500));
    expected=sort(I.trial(I.run==M.run(f)));
    assert(isequal(sort(a.trials.trial(all(a.accepted,2))),expected));
    for k=find(all(a.accepted,2))'
        j=find(I.run==M.run(f)&I.trial==a.trials.trial(k));
        assert(isscalar(j)&&~seen(j));
        assert(I.label(j)==a.trials.label(k));
        seen(j)=true;
        lab=I.label(j);
        N(s,ss,lab)=N(s,ss,lab)+1;
        for c=1:4
            z=squeeze(a.X(k,:,:,c));
            assert(all(isfinite(z),'all'));
            assert(max(abs(mean(z(t>=-.2&t<0,:),1)))<1e-8);
            sums(:,:,lab,c,s,ss)=sums(:,:,lab,c,s,ss)+z;
            squares(:,:,lab,c,s,ss)=squares(:,:,lab,c,s,ss)+z.^2;
            for ch=1:8
                for b=1:7
                    ix=(round((binStart(b)+1)*500)+1):round((binEnd(b)+1)*500);
                    assert(numel(ix)==50);
                    B(j,(ch-1)*7+b,c)=mean(z(ix,ch));
                end
            end
        end
    end
    fprintf('Feature audit %d/%d %s\n',f,height(M),M.run(f));
end
assert(all(seen)&&all(isfinite(B),'all')&&height(I)==2562);
meta=I(:,{'subject','session','runNumber','run','trial','label'});
featureNames=strings(1,56);
for ch=1:8
    for b=1:7
        featureNames((ch-1)*7+b)=sprintf('%s_%03d_%03dms',channels(ch),round(binStart(b)*1000),round(binEnd(b)*1000));
    end;
end
W=table();
for c=1:4
    A=meta;
    A.condition=repmat(c,height(A),1);
    A=[A array2table(B(:,:,c),'VariableNames',cellstr(featureNames))];
    W=[W;A];
end;
writetable(W,fullfile(out,'trial_bin_features.csv'));
rows=cell(70000,14);
nr=0;
for s=1:2
    for ss=1:3
        for c=1:4
            n1=N(s,ss,1);
            n2=N(s,ss,2);
            mu1=sums(:,:,1,c,s,ss)/n1;
            mu2=sums(:,:,2,c,s,ss)/n2;
            v1=max((squares(:,:,1,c,s,ss)-n1*mu1.^2)/(n1-1),0);
            v2=max((squares(:,:,2,c,s,ss)-n2*mu2.^2)/(n2-1),0);
            pooled=sqrt(((n1-1)*v1+(n2-1)*v2)/(n1+n2-2));
            assert(all(pooled>1e-12,'all'));
            for ch=1:8
                for ix=601:950
                    nr=nr+1;
                    rows(nr,:)={subjects(s),sessions(ss),c,channels(ch),t(ix),n1,n2,mu1(ix,ch),mu2(ix,ch),sqrt(v1(ix,ch)),sqrt(v2(ix,ch)),mu2(ix,ch)-mu1(ix,ch),(mu2(ix,ch)-mu1(ix,ch))/pooled(ix,ch),pooled(ix,ch)};
                end;
            end
        end;
    end;
end
T=cell2table(rows(1:nr,:),'VariableNames',{'subject','session','condition','channel','timeSeconds','nonDisplaced','displaced','meanND','meanD','sdND','sdD','differenceUV','cohenD','pooledSD'});
writetable(T,fullfile(out,'timepoint_summary.csv'));
save(fullfile(out,'audit_data.mat'),'B','I','sums','squares','N','t','channels','subjects','sessions','binStart','binEnd','featureNames');
fprintf('FEATURE AUDIT EXTRACTION COMPLETE: %d trial-condition vectors, %d timepoint feature summaries\n',height(W),height(T));
