function cfg = config(version)
if nargin<1, version="v2"; end
assert(ismember(string(version),["v1","v2"]),'Unknown pipeline version');
% Explicit settings for the new pipeline; independent of the current folder.
cfg.root = fileparts(fileparts(mfilename('fullpath')));
folders=dir(fullfile(cfg.root,'data'));
folders=folders([folders.isdir] & ~startsWith({folders.name},'.'));
cfg.subjects={};
for k=1:numel(folders)
    if ~isempty(dir(fullfile(folders(k).folder,folders(k).name,'*_run*_EEG.easy')))
        cfg.subjects{end+1}=folders(k).name;
    end
end
cfg.sessions = {'pre','post','retest'};
cfg.runPattern = '*_run*_EEG.easy'; % excludes training and stimulation
cfg.fs = 500;
cfg.channels = {'P3','PO3','PO7','CP5','CP1','Cz','FCz','FC1'};
cfg.band = [1 20];
cfg.filterOrder = 4;
cfg.filterPlacement = 'split'; % 'before': bandpass first; 'split': HP -> FORCe -> LP
cfg.window = [-1 1]; % half-open: [-1,1), 1000 samples
cfg.baseline = [-0.2 0]; % half-open; deliberate choice, not legacy first-sample baseline
cfg.maxAmplitudeUV = 100;
cfg.lossGuardSeconds = 2; % conservative exclusion around loss; not a proven filter bound
cfg.version = char(version);
cfg.output = fullfile(cfg.root,'output',['pipeline_' cfg.version]);
cfg.baselineOutput = fullfile(cfg.root,'output','pipeline_v1');
cfg.parsedOutput = fullfile(cfg.baselineOutput,'parsed'); % shared event metadata for v1/v2
cfg.cleaningMethod = 'none';
cfg.forceWindowSeconds = 2; % compare one full epoch with the previous 1 s windows
cfg.comparisonOutput = cfg.baselineOutput;
cfg.comparisonLabel = 'v1';
cfg.analysisLabel = cfg.version;
cfg.maxRunsPerSubjectSession = Inf;
cfg.pilot = false; % true selects the original two-participant pilot
if strcmp(cfg.version,'v2')
    if cfg.pilot, cfg.subjects = {'spe30','mle01'}; end
    cfg.cleaningMethod = 'FORCe';
    cfg.analysisLabel = sprintf('FORCe %g s',cfg.forceWindowSeconds);
    if cfg.forceWindowSeconds==2
        cfg.output = fullfile(cfg.root,'output','pipeline_v2_1');
        cfg.comparisonOutput = fullfile(cfg.root,'output','pipeline_v2');
        cfg.comparisonLabel = 'FORCe 1 s';
    end
    if strcmp(cfg.filterPlacement,'split')
        assert(cfg.forceWindowSeconds==2,'Filter-order comparison uses two-second windows');
        cfg.output = fullfile(cfg.root,'output','pipeline_v2_3');
        cfg.comparisonOutput = fullfile(cfg.root,'output','pipeline_v2_2');
        cfg.comparisonLabel = 'Previous FORCe';
        cfg.analysisLabel = 'FORCe coding fixes (v2.3)';
    end
    if ~cfg.pilot, cfg.output = [cfg.output '_all']; end
end
cfg.forceRoot = fullfile(cfg.root,'Code','FORCe');
cfg.alpha = 0.05;
end
