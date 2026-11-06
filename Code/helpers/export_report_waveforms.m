% Export condition means for the interactive waveform view from saved epochs.
% No filtering, FORCe, rejection, or classification is rerun.
% Cohort BP uses all accepted DEC_02 IDs, including sessions ineligible for CV.
% Pilot comparisons use PRE_07; matched means the four-condition intersection.
addpath(fileparts(fileparts(mfilename('fullpath'))));
root = project_root();
cfg = dataset_config();
reference = experiment_paths('PRE_01');
pilot = experiment_paths('PRE_07');
decoder = experiment_paths('DEC_02');
T = readtable(fullfile(decoder.result,'trial_metadata.csv'),'TextType','string');
subjects = sort(unique(T.subject));
sessions = ["pre","post","retest"];
records = struct('subject',{},'session',{},'condition',{},'selection',{}, ...
    'nND',{},'nD',{},'correct',{},'error',{});
total = 0;
for subject = subjects'
    for session = sessions
        ids = T(T.subject==subject & T.session==session,:);
        if isempty(ids), continue; end
        sums = zeros(1000,8,2);
        counts = zeros(1,2);
        for run = unique(ids.run,'stable')'
            rows = ids(ids.run==run,:);
            a = load(fullfile(reference.result,'processed',run+'.mat'), ...
                'epochs','trials','time','channels');
            assert(isequal(a.time(:),(-500:499)'/500));
            assert(isequal(string(a.channels(:)),string(cfg.channels(:))));
            [found,index] = ismember(rows.trial,a.trials.trial);
            assert(all(found) && all(a.trials.accepted(index)));
            assert(isequal(rows.label,a.trials.label(index)));
            for label = 1:2
                selected = index(rows.label==label);
                z = a.epochs(selected,:,:);
                assert(all(isfinite(z),'all'));
                sums(:,:,label) = sums(:,:,label) + reshape(sum(z,1),1000,8);
                counts(label) = counts(label) + numel(selected);
            end
        end
        records = add_mean(records,subject,session,1,"all",sums,counts);
        total = total + sum(counts);
        fprintf('Cohort waveform %s/%s: ND=%d D=%d\n',subject,session,counts);
    end
end
assert(total==height(T));
M = readtable(fullfile(pilot.result,'selected_manifest.csv'),'TextType','string');
for subject = sort(unique(M.subject))'
    for session = sessions
        runs = M.run(M.subject==subject & M.session==session);
        if isempty(runs), continue; end
        sums = zeros(1000,8,2,4,2);
        counts = zeros(2,4,2);
        for run = runs'
            a = load(fullfile(pilot.result,'processed',run+'.mat'), ...
                'X','accepted','trials','tc','names');
            assert(isequal(a.tc(:),(-500:499)'/500));
            assert(isequal(string(a.names),["BP_control","BP_FORCe","Split_control","Split_FORCe"]));
            rows = T(T.run==run,:);
            assert(isequal(sort(rows.trial),sort(a.trials.trial(a.accepted(:,1)))));
            common = all(a.accepted,2);
            for condition = 1:4
                for selection = 1:2
                    if selection==1, mask=a.accepted(:,condition); else, mask=common; end
                    for label = 1:2
                        selected = find(mask & a.trials.label==label);
                        z = a.X(selected,:,:,condition);
                        assert(all(isfinite(z),'all'));
                        sums(:,:,label,condition,selection) = sums(:,:,label,condition,selection) + reshape(sum(z,1),1000,8);
                        counts(label,condition,selection) = counts(label,condition,selection) + numel(selected);
                    end
                end
            end
        end
        % Confirm that the cohort and pilot BP control refer to the same trials/signals.
        r = find(string({records.subject})==subject & string({records.session})==session & ...
            [records.condition]==1 & string({records.selection})=="all");
        assert(isscalar(r));
        assert(isequal([records(r).nND records(r).nD],counts(:,1,1)'));
        for label=1:2
            if counts(label,1,1)==0, continue; end
            y=round(sums(:,:,label,1,1)/counts(label,1,1),5);
            if label==1, saved=records(r).correct; else, saved=records(r).error; end
            assert(max(abs(y-saved),[],'all')<=1e-5);
        end
        for condition = 1:4
            for selection = 1:2
                if condition==1 && selection==1, continue; end
                modes=["all","matched"];
                records = add_mean(records,subject,session,condition,modes(selection), ...
                    sums(:,:,:,condition,selection),counts(:,condition,selection)');
            end
        end
        fprintf('Pilot waveform %s/%s: four conditions, all and matched\n',subject,session);
    end
end
payload.channels = cfg.channels;
payload.sampleRate = cfg.fs;
payload.startSeconds = -1;
payload.records = records;
out = fullfile(root,'output','PRE_preprocessing_artifacts','report','waveform_means.json');
fid=fopen(out,'w','n','UTF-8');
assert(fid>=0);
cleanup=onCleanup(@() fclose(fid));
fprintf(fid,'%s',jsonencode(payload));
clear cleanup; % Close the file also when this script is run interactively.
fprintf('WAVEFORM EXPORT COMPLETE: %d participants; %d accepted cohort trials; %d series\n', ...
    numel(subjects),total,numel(records));

function records = add_mean(records,subject,session,condition,selection,sums,counts)
r = struct('subject',subject,'session',session,'condition',condition,'selection',selection, ...
    'nND',counts(1),'nD',counts(2),'correct',[],'error',[]);
if counts(1)>0, r.correct=round(sums(:,:,1)/counts(1),5); end
if counts(2)>0, r.error=round(sums(:,:,2)/counts(2),5); end
records(end+1)=r;
end
