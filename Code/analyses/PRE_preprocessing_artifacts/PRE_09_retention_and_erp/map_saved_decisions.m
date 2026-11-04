% PRE_09: Retention and matched ERP comparison.
% Workflow, execution order and interpretation: ../README.md#pre_09.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Map saved one-second FORCe pilot decisions; no raw preprocessing or cleaning is rerun.
root = project_root();
out=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_09_retention_and_erp','quality');
source=fullfile(root,'output','PRE_preprocessing_artifacts','PRE_07_boundary_analysis');
M=readtable(fullfile(source,'selected_manifest.csv'),'TextType','string');
rows=cell(15000,14);
n=0;
for f=1:height(M)
    a=load(fullfile(source,'processed',M.run(f)+'.mat'),'accepted','eligible','reason','trials','names','X','tc');
    assert(isequal(string(a.names),["BP_control","BP_FORCe","Split_control","Split_FORCe"]));
    assert(height(a.trials)==size(a.accepted,1));
    assert(all(~any(a.accepted,2) | a.eligible));
    t=a.tc;
    response=t>=.4 & t<.8;
    for k=1:height(a.trials)
        for c=1:4
            z=squeeze(a.X(k,:,:,c));
            finite=all(isfinite(z),'all');
            pk=NaN;
            rp=NaN;
            st=NaN;
            if finite
                pk=max(abs(z),[],'all');
                rp=max(abs(z(response,:)),[],'all');
                st=max(abs(diff(z)),[],'all');
            end
            if a.accepted(k,c)
                assert(finite && pk<=100);
            end
            n=n+1;
            rows(n,:)={M.subject(f),M.session(f),M.runNumber(f),M.run(f),a.trials.trial(k),a.trials.label(k),c,string(a.names{c}),a.eligible(k),a.accepted(k,c),a.reason(k,c),pk,rp,st};
        end;
    end
    fprintf('Mapped saved decisions %d/%d %s\n',f,height(M),M.run(f));
end
D=cell2table(rows(1:n,:),'VariableNames',{'subject','session','runNumber','run','trial','label','condition','conditionName','eligible','accepted','reason','finalPeakAbsUV','responsePeakAbsUV','finalMaxStepUV'});
writetable(D,fullfile(out,'saved_trial_decisions.csv'));
fprintf('SAVED DECISION EXPORT COMPLETE: %d rows\n',height(D));
