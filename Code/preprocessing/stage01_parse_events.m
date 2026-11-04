% Stage 1: parse and validate events; no EEG signal processing.
% Inputs: run-named raw EEG and matching same-day mouse logs.
% Outputs: shared trial tables and manifest under cfg.parsedOutput.
% Reuse the existing manifest; parsing is independent of FORCe cleaning.
% Preserve raw indices and trial identity; flag ambiguous sequences rather
% than silently assigning a condition. Original recordings remain untouched.
pipelineDir=fileparts(mfilename('fullpath'));
codeDir=fileparts(pipelineDir);
addpath(codeDir,pipelineDir,fullfile(codeDir,'helpers'));
if ~exist('cfg','var') || ~isstruct(cfg) || ~isfield(cfg,'experimentId')
    cfg=dataset_config();
end
out=cfg.parsedOutput;
if isfile(fullfile(out,'manifest.csv'))
    fprintf('Reusing parsed events: %s\n',out);
    return;
end
if ~isfolder(out), mkdir(out); end
manifest=table();
for s=1:numel(cfg.subjects)
    subject=cfg.subjects{s}; folder=fullfile(cfg.root,'data',subject);
    files=dir(fullfile(folder,cfg.runPattern));
    for f=1:numel(files)
        name=files(f).name; rawPath=fullfile(folder,name);
        suffix=extractAfter(name,15); suffix=erase(suffix,'_EEG.easy');
        logs=dir(fullfile(folder,[name(1:8) '*' char(suffix) '_tdcserror_.csv']));
        % Aborted starts can leave header-only CSVs with the same run suffix.
        usable=false(size(logs));
        for j=1:numel(logs)
            candidate=readtable(fullfile(folder,logs(j).name),'VariableNamingRule','preserve');
            usable(j)=ismember('event',candidate.Properties.VariableNames) && ...
                height(candidate)>0 && any(candidate.event==100);
        end
        logs=logs(usable);
        mouseCandidates=string({logs.name});
        if numel(logs)>1
            warning('Ambiguous mouse logs for %s; retaining run as unvalidated.',name);
            logs=logs([]);
        end
        mousePath='';
        if isempty(logs)
            mouse=table([],[],[],[],[],'VariableNames',{'trial','time','event','x_target','y_target'});
        else
            mousePath=fullfile(folder,logs(1).name);
            mouse=readtable(mousePath,'VariableNamingRule','preserve');
        end
        raw=readmatrix(rawPath,'FileType','text');
        [trials,events,info]=parse_run(raw,mouse,cfg);
        info.rawPath=rawPath; info.mousePath=mousePath; info.subject=subject;
        info.mouseCandidates=mouseCandidates;
        parts=regexp(name,'^(\d{8})\d{6}_(\w+)_(pre|post|retest)_run(\d+)_EEG.easy$','tokens','once');
        assert(~isempty(parts),'Unrecognized run filename: %s',name);
        info.recordingDate=parts{1}; info.session=parts{3}; info.runNumber=str2double(parts{4});
        trials.subject=repmat(string(subject),height(trials),1);
        trials.session=repmat(string(info.session),height(trials),1);
        trials.recordingDate=repmat(string(info.recordingDate),height(trials),1);
        trials.runNumber=repmat(info.runNumber,height(trials),1);
        stem=erase(name,'.easy'); parsedPath=fullfile(out,[stem '.mat']);
        save(parsedPath,'trials','events','info','cfg');
        writetable(trials,fullfile(out,[stem '_trials.csv']));
        manifest=[manifest;table(string(subject),string(info.session),string(info.recordingDate),info.runNumber,string(stem),string(parsedPath),...
            height(trials),sum(trials.valid),'VariableNames',...
            {'subject','session','recordingDate','runNumber','run','parsedPath','trials','validTrials'})]; %#ok<AGROW>
        fprintf('%s: %d/%d valid event sequences\n',stem,sum(trials.valid),height(trials));
    end
end
writetable(manifest,fullfile(out,'manifest.csv'));
