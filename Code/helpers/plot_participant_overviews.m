% Participant views of Cz and FCz across sessions, for exploratory inspection.
codeDir=fileparts(fileparts(mfilename('fullpath'))); addpath(codeDir); cfg=config();
source=fullfile(cfg.output,'figures','by_session');
out=fullfile(cfg.output,'figures','by_participant'); if ~isfolder(out), mkdir(out); end
for subject=string(cfg.subjects)
    fig=figure('Visible','off','Position',[100 100 1200 1050]); tiledlayout(3,2);
    for ss=1:numel(cfg.sessions)
        session=cfg.sessions{ss}; file=fullfile(source,subject+"_"+session+"_averages.mat");
        for name=["Cz","FCz"]
            nexttile;
            if ~isfile(file), title(session+" / "+name+": insufficient trials"); axis off; continue; end
            d=load(file); ch=find(strcmp(cfg.channels,name));
            h=plot(d.time,d.correct(:,ch),'b',d.time,d.displaced(:,ch),'r',d.time,d.difference(:,ch),'k');
            xline(0,'k:','HandleVisibility','off'); yline(0,'k:','HandleVisibility','off');
            xlim([-1 1]); xlabel('Time from movement (s)'); ylabel('microvolts');
            title(sprintf('%s / %s: non-displaced n=%d, displaced n=%d',session,name,sum(d.labels==1),sum(d.labels==2)));
            if ss==1 && name=="Cz"
                lg=legend(h,{'Non-displaced','Displaced','Displaced - non-displaced'}); lg.Layout.Tile='south';
            end
        end
    end
    sgtitle(subject+" / "+cfg.analysisLabel+" / exploratory participant review");
    exportgraphics(fig,fullfile(out,subject+"_overview.png")); close(fig);
end
