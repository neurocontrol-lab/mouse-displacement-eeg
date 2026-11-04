function cfg = config(experimentId)
% Explicit historical experiment settings; use dataset_config for shared conventions.
% Cached historical results remain authoritative where FORCe code has since changed.
% Example: cfg = config('PRE_02'); stage02_preprocess_epochs
if nargin < 1, experimentId = 'PRE_06'; end
addpath(fileparts(fileparts(mfilename('fullpath'))));
cfg = dataset_config();
assert(ismember(string(experimentId), compose('PRE_%02d', 1:6)), ...
    'Original stages support PRE_01 through PRE_06');
paths = experiment_paths(experimentId);
cfg.experimentId = char(experimentId);
cfg.output = paths.result;
cfg.analysisLabel = cfg.experimentId;
cfg.maxRunsPerSubjectSession = Inf;
cfg.filterPlacement = 'before';
cfg.forceWindowSeconds = 2;
cfg.cleaningMethod = 'FORCe';
cfg.pilot = ~ismember(string(experimentId), ["PRE_01", "PRE_06"]);
if cfg.pilot, cfg.subjects = {'spe30','mle01'}; end
switch char(experimentId)
    case 'PRE_01'
        cfg.cleaningMethod = 'none';
        referenceId = 'PRE_01';
    case 'PRE_02'
        cfg.forceWindowSeconds = 1;
        referenceId = 'PRE_01';
    case 'PRE_03'
        referenceId = 'PRE_02';
    case 'PRE_04'
        cfg.filterPlacement = 'split';
        referenceId = 'PRE_03';
    case {'PRE_05','PRE_06'}
        cfg.filterPlacement = 'split';
        referenceId = 'PRE_04';
end
reference = experiment_paths(referenceId);
cfg.comparisonOutput = reference.result;
cfg.comparisonLabel = referenceId;
end
