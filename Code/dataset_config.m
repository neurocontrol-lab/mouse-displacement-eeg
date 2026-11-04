function cfg = dataset_config()
% Shared dataset conventions; no experiment-specific cleaning is selected here.
cfg.root = project_root();
cfg.fs = 500;
cfg.channels = {'P3','PO3','PO7','CP5','CP1','Cz','FCz','FC1'};
cfg.sessions = {'pre','post','retest'};
cfg.runPattern = '*_run*_EEG.easy';
cfg.band = [1 20];
cfg.filterOrder = 4;
cfg.window = [-1 1];
cfg.baseline = [-0.2 0];
cfg.maxAmplitudeUV = 100;
cfg.lossGuardSeconds = 2;
cfg.alpha = 0.05;
reference = experiment_paths('PRE_01');
cfg.baselineOutput = reference.result;
cfg.parsedOutput = fullfile(reference.result, 'parsed');
cfg.forceRoot = fullfile(cfg.root, 'Code', 'FORCe');
folders = dir(fullfile(cfg.root, 'data'));
cfg.subjects = {};
for k = 1:numel(folders)
    if folders(k).isdir && ~startsWith(folders(k).name, '.') && ...
            ~isempty(dir(fullfile(folders(k).folder, folders(k).name, cfg.runPattern)))
        cfg.subjects{end+1} = folders(k).name;
    end
end
end
