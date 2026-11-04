% DEC_01: Pilot decoders.
% Workflow, execution order and interpretation: README.md in this folder.
% Inputs/outputs resolve through the permanent experiment registry.
% Resolve the repository before reading cached experiment inputs.
addpath(fileparts(fileparts(fileparts(fileparts(mfilename('fullpath'))))));
% Export all audited channel sets and the Cz/FCz reference for classification.
% Use the saved final epochs; this does not rerun preprocessing or FORCe.
% Feature interval: [0.2, 0.9) s at 500 Hz, with channels kept separate.
root = project_root();
out = fullfile(root, 'output', 'DEC_decoding', 'DEC_01_pilot_decoders');
src = fullfile(root, 'output', 'PRE_preprocessing_artifacts', 'PRE_07_boundary_analysis');
I = readtable(fullfile(root, 'output', 'PRE_preprocessing_artifacts', 'PRE_09_retention_and_erp', 'matched_erp', ...
'matched_trial_ids.csv'), 'TextType', 'string');
M = readtable(fullfile(src, 'selected_manifest.csv'), 'TextType', 'string');
rawFeatures = nan(height(I), 700, 4);
allFeatures = nan(height(I), 350, 8, 4);
seen = false(height(I), 1);

for f = 1:height(M)
    a = load(fullfile(src, 'processed', M.run(f) + '.mat'), ...
    'X', 'tc', 'trials', 'accepted');
    assert(isequal(a.tc(:), (-500:499)' / 500));
    js = find(I.run == M.run(f));
    assert(isequal(sort(I.trial(js)), ...
    sort(a.trials.trial(all(a.accepted, 2)))));
    for j = js'
        k = find(a.trials.trial == I.trial(j));
        assert(isscalar(k) && all(a.accepted(k, :)) && ...
        I.label(j) == a.trials.label(k));
        seen(j) = true;
        allFeatures(j, :, :, :) = a.X(k, 601:950, :, :);
        for c = 1:4
            z = squeeze(a.X(k, 601:950, [6 7], c));
            assert(isequal(size(z), [350 2]));
            % First 350 samples are Cz; next 350 are FCz.
            rawFeatures(j, :, c) = reshape(z, 1, 700);
        end
    end
    fprintf('Classification export %d/%d %s\n', f, height(M), M.run(f));
end
assert(all(seen) && all(isfinite(rawFeatures), 'all') && height(I) == 2562);
assert(all(isfinite(allFeatures), 'all'));

% Confirm that binning these samples reproduces the prior central feature audit.
B = load(fullfile(root, 'output', 'FEA_features_repeatability', 'FEA_01_feature_audit', 'audit_data.mat'), 'B', 'I');
assert(isequal(I.run, B.I.run) && isequal(I.trial, B.I.trial));
for c = 1:4
    v = zeros(height(I), 14);
    for ch = 1:2
        for b = 1:7
            ix = (ch - 1) * 350 + (b - 1) * 50 + (1:50);
            v(:, (ch - 1) * 7 + b) = mean(rawFeatures(:, ix, c), 2);
        end
    end
    assert(max(abs(v - B.B(:, 36:49, c)), [], 'all') < 1e-10);
end

writetable(I, fullfile(out, 'trial_metadata.csv'));
fs = 500;
sampleTimes = (100:449)' / 500;
channels = {'Cz', 'FCz'};
save(fullfile(out, 'central_features.mat'), ...
'rawFeatures', 'fs', 'sampleTimes', 'channels', '-v7');
allChannels = {'P3', 'PO3', 'PO7', 'CP5', 'CP1', 'Cz', 'FCz', 'FC1'};
% Check every channel's 100 ms means against the original feature audit.
for c = 1:4
    v = zeros(height(I), 56);
    for ch = 1:8
        for b = 1:7
            v(:, (ch - 1) * 7 + b) = mean(allFeatures(:, (b - 1) * 50 + (1:50), ch, c), 2);
        end
    end
    assert(max(abs(v - B.B(:, :, c)), [], 'all') < 1e-10);
end
save(fullfile(out, 'all_channel_features.mat'), ...
'allFeatures', 'fs', 'sampleTimes', 'allChannels', '-v7');
fprintf('CLASSIFICATION EXPORT COMPLETE: 2562 trials x 350 samples x 8 channels x 4 conditions\n');
