function paths = experiment_paths(experimentId)
% Resolve permanent experiment IDs using the shared experiment directory map.
root = project_root();
registry = jsondecode(fileread(fullfile(root, 'Code', 'experiments.json')));
key = char(experimentId);
assert(isfield(registry, key), 'Unknown experiment ID: %s', key);
paths.root = root;
paths.result = fullfile(root, registry.(key).result);
paths.code = fullfile(root, registry.(key).code);
end
