function [clean, status] = clean_epoch_force(epoch, cfg, chanlocs)
% Clean a samples x channels epoch using the configured FORCe window length.
% With 2 s, the entire epoch is cleaned together, without an internal join.
% A failed window rejects the whole epoch.
assert(cfg.fs==500 && isequal(size(epoch),[1000 numel(cfg.channels)]), ...
    'FORCe expects a two-second epoch at 500 Hz');
assert(isequal(lower(string({chanlocs.labels})),lower(string(cfg.channels))), ...
    'FORCe channel order mismatch');
clean=nan(size(epoch)); status="ok";
if ~isreal(epoch) || any(~isfinite(epoch),'all')
    status="invalid_input"; return;
end
windowSamples=round(cfg.forceWindowSeconds*cfg.fs);
assert(ismember(cfg.forceWindowSeconds,[1 2]),'FORCe window must be 1 or 2 seconds');
for w=1:size(epoch,1)/windowSamples
    ix=(w-1)*windowSamples+(1:windowSamples); x=epoch(ix,:)';
    % Retain the pilot policy: exclude the unresolved interpolation branch.
    if any(max(x,[],2)>200)
        status="channel_threshold";
    elseif any(std(x,0,2)<1e-12)
        status="flat_channel";
    else
        try
            % Suppress the library's verbose console output.
            evalc('[y, details]=FORCe(x,cfg.fs,chanlocs,0);');
            status=string(details.status);
            if ~isequal(size(y),size(x)) || ~isreal(y) || any(~isfinite(y),'all')
                status="invalid_output";
            elseif sqrt(mean(y.^2,'all'))<1e-12
                status="zero_output";
            end
            if status=="ok", clean(ix,:)=y'; end
        catch ME
            warning('FORCe:CleaningFailed','%s',ME.message);
            if strcmp(ME.identifier,'FORCe:InvalidFeature')
                status="invalid_feature";
            else
                status="failed";
            end
        end
    end
    if status~="ok", clean(:)=NaN; return; end
end
end
