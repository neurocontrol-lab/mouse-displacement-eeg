function test_event_parser()
here=fileparts(fileparts(mfilename('fullpath'))); addpath(here,fullfile(here,'helpers')); cfg=dataset_config();
folder=fullfile(cfg.root,'data','mle01');
raw=readmatrix(fullfile(folder,'20181113091555_mle01_retest_run3_EEG.easy'),'FileType','text');
mouse=readtable(fullfile(folder,'20181113091557_mle01_retest_run3_tdcserror_.csv'));
[t,e]=parse_run(raw,mouse,cfg);
assert(height(t)==100 && all(t.valid(1:99)) && ~t.valid(100)); % mouse log stops at 99
assert(all(t.label([76 78])==2));
assert(isequal(t.movementSample([76 78]),[178531;183204]));
assert(isequal(t.displacementSample([76 78]),[178564;183238]));
assert(sum(e.code==500)==34);
% A repeated marker is one event; a missing task event makes the trial invalid.
raw(178565,12)=500; [t2,e2]=parse_run(raw,mouse,cfg);
assert(t2.label(76)==2 && sum(e2.code==500)==34);
raw(178564:178565,12)=0; t3=parse_run(raw,mouse,cfg);
assert(~t3.valid(76) && isnan(t3.label(76)));
fprintf('PASS: known two-label regression, repeated marker and missing event.\n');
end
