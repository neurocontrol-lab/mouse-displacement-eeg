function test_force_integration()
% Optional quick check on one real epoch; no pipeline outputs are written.
here=fileparts(fileparts(mfilename('fullpath'))); addpath(here,fullfile(here,'helpers'));
cfg=dataset_config(); cfg.forceWindowSeconds=2; addpath(cfg.forceRoot,fullfile(cfg.forceRoot,'mex-files'));
% Focused spectrum regression: orientation and bin labels, retaining legacy magnitudes.
signal=cos(2*pi*10*(0:499)/500); spectrum=powerspectrum(signal,500);
assert(isequal(spectrum,powerspectrum(signal',500)));
assert(max(abs(spectrum(1,:)-(0:255)*500/512))<1e-12);
transform=fft(signal,512)/500;
assert(max(abs(spectrum(2,:)-2*abs(transform(1:256))))<1e-12);
previous=dwtmode('status','nodisp'); dwtmode('sym','nodisp');
cleanup=onCleanup(@() dwtmode(previous,'nodisp'));
f=dir(fullfile(cfg.baselineOutput,'processed','*_mle01_pre_run1_EEG.mat'));
assert(~isempty(f),'PRE_01 reference epochs are required for this optional check');
p=load(fullfile(f(1).folder,f(1).name)); k=find(p.trials.accepted,1);
x=squeeze(p.epochs(k,:,:)); loc=load(fullfile(cfg.root,'Code','resources','chanlocs8.mat'));
[y,status]=clean_epoch_force(x,cfg,loc.chanlocs8);
assert(status=="ok" && isequal(size(y),size(x)) && all(isfinite(y),'all'));
x(1)=NaN; [y,status]=clean_epoch_force(x,cfg,loc.chanlocs8);
assert(status=="invalid_input" && all(isnan(y),'all'));
fprintf('PASS: real-epoch cleaning and invalid-input handling.\n');
end
