% DEC_03: Graz-style feature comparison.
% Workflow, execution order and interpretation: README.md in this folder.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Export full [-1,1) s accepted epochs for training-fold r-squared selection.
% Trial inclusion is exactly the saved full-dataset no-FORCe analysis.
root = project_root();
parent=fullfile(root,'output','DEC_decoding','DEC_02_full_cohort_decoders');
graz = experiment_paths('DEC_03');
out=fullfile(graz.result,'raw_epochs');
if ~isfolder(out)
    mkdir(out);
end
I=readtable(fullfile(parent,'trial_metadata.csv'),'TextType','string');
A=load(fullfile(parent,'features.mat'),'features','channels');
subjects=unique(I.subject,'stable');
done=0;
for subject=subjects'
    for session=["pre","post","retest"]
        rows=find(I.subject==subject & I.session==session);
        if isempty(rows)
            continue;
        end
        destination=fullfile(out,subject+"_"+session+".mat");
        if isfile(destination)
            check=load(destination,'globalRows');
            assert(isequal(check.globalRows,rows));
            done=done+1;
            fprintf('Full-epoch export %d reused %s/%s\n',done,subject,session);
            continue;
        end
        rawFeatures=nan(numel(rows),8000);
        runs=unique(I.run(rows),'stable');
        for run=runs'
            a=load(fullfile(root,'output','PRE_preprocessing_artifacts','PRE_01_no_force_reference','processed',run+'.mat'), ...
            'epochs','time','trials','channels');
            assert(isequal(a.channels,A.channels) && isequal(a.time(:),(-500:499)'/500));
            positions=find(I.run(rows)==run);
            for position=positions'
                globalRow=rows(position);
                k=find(a.trials.trial==I.trial(globalRow));
                assert(isscalar(k) && a.trials.accepted(k) && a.trials.label(k)==I.label(globalRow));
                z=squeeze(a.epochs(k,:,:));
                assert(all(isfinite(z),'all'));
                rawFeatures(position,:)=reshape(z,1,8000);
                means=reshape(mean(reshape(z(601:950,:),50,7,8),1),1,56);
                assert(max(abs(means-A.features(globalRow,:)))<1e-10);
            end
        end
        assert(all(isfinite(rawFeatures),'all'));
        globalRows=rows;
        channels=A.channels;
        sampleTimes=(-500:499)/500;
        save(destination,'rawFeatures','globalRows','channels','sampleTimes','-v7');
        done=done+1;
        fprintf('Full-epoch export %d %s/%s: %d matched trials\n',done,subject,session,numel(rows));
    end
end
fprintf('GRAZ FULL-EPOCH EXPORT COMPLETE: %d participant/sessions\n',done);
