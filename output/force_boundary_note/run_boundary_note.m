% Isolated four-condition pilot: production scripts and old outputs are unchanged.
root='C:/Users/satya/OneDrive/Documents/[S. Perdikis] ErrPo EEG of Mouse Movements/ErrpAnalysis';
code=fullfile(root,'Code');addpath(code,fullfile(code,'helpers'));cfg=config();cfg.subjects={'spe30','mle01'};
out=fullfile(root,'output','force_boundary_note');if ~isfolder(out),mkdir(out);end
addpath(cfg.forceRoot,fullfile(cfg.forceRoot,'mex-files'));dwtmode('sym','nodisp');rng(0);
loc=load(fullfile(code,'resources','chanlocs8.mat'));loc=loc.chanlocs8;
M=readtable(fullfile(cfg.parsedOutput,'manifest.csv'),'TextType','string');M=M(ismember(M.subject,string(cfg.subjects)) & M.validTrials>0,:);M=sortrows(M,{'subject','session','recordingDate','runNumber','run'});writetable(M,fullfile(out,'selected_manifest.csv'));
[bh,ah]=butter(4,1/250,'high');[bl,al]=butter(4,20/250,'low');[bb,ab]=butter(4,[1 20]/250);
time=(-750:749)/500;crop=time>=-1 & time<1;tc=time(crop);base=tc>=-.2 & tc<0;
names={'BP_control','BP_FORCe','Split_FORCe','Split_control'};processed=fullfile(out,'processed');if ~isfolder(processed),mkdir(processed);end
for f=1:height(M)
 destination=fullfile(processed,M.run(f)+'.mat');if isfile(destination),fprintf('Already saved %s\n',M.run(f));continue;end
 p=load(fullfile(cfg.parsedOutput,M.run(f)+'.mat'));trials=p.trials;raw=readmatrix(fullfile(root,'data',M.subject(f),M.run(f)+'.easy'),'FileType','text');eeg=raw(:,1:8)/1000;
 bad=raw(:,12)==255 | any(~isfinite(eeg),2);gap=find(diff(raw(:,13))~=2);bad(gap)=true;bad(gap+1)=true;edges=diff([false;~bad;false]);first=find(edges==1);last=find(edges==-1)-1;
 hp=nan(size(eeg));bp=hp;hpLp=hp;quality=true(size(bad));guard=1000;
 for j=1:numel(first)
 ix=first(j):last(j);if numel(ix)<=2*guard,continue;end
 hp(ix,:)=filtfilt(bh,ah,eeg(ix,:));bp(ix,:)=filtfilt(bb,ab,eeg(ix,:));hpLp(ix,:)=filtfilt(bl,al,hp(ix,:));quality(first(j)+guard:last(j)-guard)=false;
 end
 n=height(trials);X=nan(n,1000,8,4);preSplit=nan(n,1500,8);preBP=preSplit;continuousSplit=nan(n,1000,8);
 accepted=false(n,4);eligible=false(n,1);reason=repmat("invalid_event",n,4);centring=nan(n,3,8);reconstruction=centring;inputMeans=centring;cleanMeans=centring;
 for k=1:n
 if ~trials.valid(k),continue;end
 ix=trials.movementSample(k)+(-750:749);if min(ix)<1 || max(ix)>size(raw,1),reason(k,:)="out_of_bounds";continue;end
 if any(quality(ix)),reason(k,:)="gap_or_filter_guard";continue;end
 eligible(k)=true;H=hp(ix,:);B=bp(ix,:);L=hpLp(ix,:);rejoined=[H(1:500,:);H(501:1000,:);H(1001:1500,:)];assert(isequal(rejoined,H));
 Y=cell(1,4);Y{1}=B;Y{4}=filtfilt(bl,al,rejoined);[Y{2},s2]=clean3(B,cfg,loc);[S,s3]=clean3(H,cfg,loc);reason(k,:)=["ok",s2,s3,"ok"];
 if s2=="ok",preBP(k,:,:)=Y{2};end
 if s3=="ok",preSplit(k,:,:)=S;Y{3}=filtfilt(bl,al,S);end
 continuousSplit(k,:,:)=L(crop,:)-mean(L(crop & time>=-.2 & time<0,:),1);
 for v=1:4
 if isempty(Y{v}),continue;end
 z=Y{v}(crop,:);z=z-mean(z(base,:),1);X(k,:,:,v)=z;
 if any(~isfinite(z),'all'),reason(k,v)="nonfinite";elseif max(abs(z),[],'all')>100,reason(k,v)="amplitude";else,accepted(k,v)=true;end
 end
 if sum(eligible(1:k))<=3
 for w=1:3
 wi=(w-1)*500+(1:500);inputMeans(k,w,:)=mean(H(wi,:),1);if s3=="ok",cleanMeans(k,w,:)=mean(S(wi,:),1);end
 [ic,mix,packs]=applyOnlineICAmethodWaveNowsobi(H(wi,:)');tn=get(packs{1},'tN');Z=zeros(8,500);
 for ch=1:8
 pack=packs{ch};for node=1:numel(tn)
 if tn(node)==3,coef=mix{node}*ic{node};else,coef=ic{node};end
 pack=write(pack,'data',tn(node),coef(ch,:));end;Z(ch,:)=wprec(pack);end
 centring(k,w,:)=mean(Z'-H(wi,:),1);reconstruction(k,w,:)=sqrt(mean((Z'-H(wi,:)).^2,1));
 end
 end
 end
 save(destination,'X','preSplit','preBP','continuousSplit','accepted','eligible','reason','trials','time','tc','names','cfg','centring','reconstruction','inputMeans','cleanMeans','-v7.3');
 fprintf('%d/%d %s eligible %d accepted %s\n',f,height(M),M.run(f),sum(eligible),mat2str(sum(accepted)));
end
fprintf('PROCESSING COMPLETE\n');
function [Y,status]=clean3(x,cfg,loc)
Y=[];status="ok";clean=nan(size(x));
for w=1:3
ix=(w-1)*500+(1:500);a=x(ix,:)';
if any(max(a,[],2)>200),status="channel_threshold";return;end
if any(std(a,0,2)<1e-12),status="flat_channel";return;end
try
evalc('[b,d]=FORCe(a,cfg.fs,loc,0);');
if string(d.status)~="ok",status=string(d.status);return;end
if ~isequal(size(b),size(a)) || any(~isfinite(b),'all') || ~isreal(b),status="invalid_output";return;end
if sqrt(mean(b.^2,'all'))<1e-12,status="zero_output";return;end
clean(ix,:)=b';
catch ME,status="failed_"+string(ME.identifier);return;end
end
Y=clean;
end
