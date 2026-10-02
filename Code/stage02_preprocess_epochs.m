% Stage 2: prepare, clean and quality-check movement-locked EEG epochs.
% Inputs: validated stage-1 metadata and original recordings (nV).
% Processing: high-pass valid segments, extract two-second epochs, apply
% FORCe, low-pass, baseline and reject. The before setting retains the earlier
% bandpass-first pipeline. Preserve all trial rows and rejection reasons.
% Outputs: final trials x time x channels epochs and trial rejection reasons.
% Rejected rows remain NaN. Default v2 includes all eligible participant runs;
% existing v1 outputs remain read-only. Rerunning recomputes v2 outputs.

% Stage 2a: setup
codeDir=fileparts(mfilename('fullpath')); addpath(codeDir,fullfile(codeDir,'helpers'));
cfg=config();
manifestPath=fullfile(cfg.parsedOutput,'manifest.csv');
if ~isfile(manifestPath), stage01_parse_events; end
out=fullfile(cfg.output,'processed');
assert(~strcmp(cfg.output,cfg.baselineOutput),'Stage 2 integration must not overwrite v1');
if ~isfolder(out), mkdir(out); end
addpath(cfg.forceRoot,fullfile(cfg.forceRoot,'mex-files'));
assert(strcmp(which('FORCe'),fullfile(cfg.forceRoot,'FORCe.m')),'Unexpected FORCe on path');
assert(~isempty(which('wpdec')),'Wavelet Toolbox required');
previousWaveletMode=dwtmode('status','nodisp'); dwtmode('sym','nodisp');
waveletCleanup=onCleanup(@() dwtmode(previousWaveletMode,'nodisp'));
locations=load(fullfile(cfg.root,'Code','resources','chanlocs8.mat')); chanlocs=locations.chanlocs8;
assert(all(isfinite([[chanlocs.X];[chanlocs.Y];[chanlocs.Z]]),'all'),'Invalid coordinates');
manifest=readtable(manifestPath,'TextType','string','Delimiter',',','VariableNamingRule','preserve');
manifest=sortrows(manifest,{'subject','session','recordingDate','runNumber','run'});
selected=false(height(manifest),1);
for subject=string(cfg.subjects)
    for session=string(cfg.sessions)
        rows=find(manifest.subject==subject & manifest.session==session & manifest.validTrials>0);
        selected(rows(1:min(numel(rows),cfg.maxRunsPerSubjectSession)))=true;
    end
end
manifest=manifest(selected,:);
% Resolve parsed files in the current project after a folder move.
manifest.parsedPath=string(fullfile(cfg.parsedOutput,manifest.run+".mat"));
assert(~isempty(manifest),'No eligible runs');
writetable(manifest,fullfile(cfg.output,'selected_manifest.csv'));
assert(ismember(cfg.filterPlacement,{'before','split'}),'Unknown filter placement');
if strcmp(cfg.filterPlacement,'split')
    [b,a]=butter(cfg.filterOrder,cfg.band(1)/(cfg.fs/2),'high');
    [bLow,aLow]=butter(cfg.filterOrder,cfg.band(2)/(cfg.fs/2),'low');
else
    [b,a]=butter(cfg.filterOrder,cfg.band/(cfg.fs/2),'bandpass');
end
offsets=round(cfg.window(1)*cfg.fs):round(cfg.window(2)*cfg.fs)-1;
time=offsets/cfg.fs; base=time>=cfg.baseline(1) & time<cfg.baseline(2);
assert(any(base),'Empty baseline interval'); channels=cfg.channels;
for f=1:height(manifest)
    % Stage 2b: load recording
    runStarted=tic;
    p=load(manifest.parsedPath(f)); trials=p.trials; info=p.info;
    destination=fullfile(out,manifest.run(f)+".mat");
    % Raw paths in saved metadata may refer to the previous project folder.
    info.rawPath=fullfile(cfg.root,'data',char(manifest.subject(f)),char(manifest.run(f)+".easy"));
    raw=readmatrix(info.rawPath,'FileType','text'); eeg=raw(:,1:8)/1000;
    % Stage 2c: filter valid segments and guard gaps
    bad=raw(:,12)==255 | any(~isfinite(eeg),2);
    gap=find(diff(raw(:,13))~=1000/cfg.fs); bad(gap)=true; bad(gap+1)=true;
    edges=diff([false;~bad;false]); first=find(edges==1); last=find(edges==-1)-1;
    filtered=nan(size(eeg)); quality=true(size(bad)); guard=round(cfg.lossGuardSeconds*cfg.fs);
    for j=1:numel(first)
        ix=first(j):last(j);
        if numel(ix)<=max(3*(max(numel(a),numel(b))-1),2*guard), continue; end
        filtered(ix,:)=filtfilt(b,a,eeg(ix,:));
        quality(first(j)+guard:last(j)-guard)=false;
    end
    % Stage 2d: extract eligible epochs
    epochs=nan(height(trials),numel(time),numel(channels));
    trials.accepted=false(height(trials),1); trials.rejection=trials.reason;
    for k=1:height(trials)
        if ~trials.valid(k), continue; end
        ix=trials.movementSample(k)+offsets;
        if min(ix)<1 || max(ix)>size(raw,1), trials.rejection(k)="epoch_out_of_bounds"; continue; end
        if any(quality(ix)), trials.rejection(k)="data_loss_gap_or_filter_edge"; continue; end
        x=filtered(ix,:);
        % Stage 2e: FORCe cleaning
        if strcmp(cfg.cleaningMethod,'FORCe')
            [x,status]=clean_epoch_force(x,cfg,chanlocs);
            if status~="ok"
                trials.rejection(k)="force_"+status; continue;
            end
        end
        % Stage 2f: application filter, baseline and final rejection
        if strcmp(cfg.filterPlacement,'split')
            % Zero-phase low-pass on each cleaned epoch; filtfilt handles endpoints.
            % Unlike the reference's continuous filter, epoch-edge effects remain possible.
            x=filtfilt(bLow,aLow,x);
        end
        x=x-mean(x(base,:),1);
        if any(~isfinite(x),'all'), trials.rejection(k)="nonfinite"; continue; end
        if max(abs(x),[],'all')>cfg.maxAmplitudeUV, trials.rejection(k)="amplitude"; continue; end
        epochs(k,:,:)=x; trials.accepted(k)=true; trials.rejection(k)="ok";
    end
    % Stage 2g: save results
    if strcmp(cfg.filterPlacement,'split')
        processingNote='Continuous 1 Hz HP -> 2 s FORCe -> epoch 20 Hz LP -> baseline; interpolation excluded.';
    else
        processingNote=sprintf('1-20 Hz before FORCe; %g s cleaning windows; interpolation windows excluded.',cfg.forceWindowSeconds);
    end
    processingSeconds=toc(runStarted);
    save(destination,'epochs','time','channels','trials','info','cfg','processingNote','processingSeconds','-v7.3');
    writetable(trials,fullfile(out,manifest.run(f)+"_quality.csv"));
    fprintf('%s: accepted %d of %d trials\n',manifest.run(f),sum(trials.accepted),height(trials));
end
clear waveletCleanup;
