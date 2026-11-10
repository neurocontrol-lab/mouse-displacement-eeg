"""Build portable research-report overviews from saved summaries; no analysis refits.

Run from the repository root: python Code/helpers/build_web_reports.py
The resulting index.html files embed displayed figures and aggregate data so they
work with file:// and GitHub HTMLPreview without fetching raw/trial-level data.
"""

from pathlib import Path
import base64
import csv
import html
import json
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research_paths import ROOT, EXPERIMENTS, result_path
import audit_web_report
import erp_web_report

REPORTS = {
    audit_web_report.CATEGORY: {"title": "Data audit"},
    "PRE_preprocessing_artifacts": {
        "title": "Preprocessing and artifact handling",
        "summary": "The primary BP no-FORCe waveform view covers all 25 participants. Four-condition comparisons remain limited to mle01 and spe30, with all accepted or matched trials. Sharp-join attenuation alone does not demonstrate neural-signal preservation.",
        "pdf": "FORCe_retention_and_ErrP_pilot_note.pdf",
        "figure_descriptions": {
            "filtering_effects": (
                "Top: median and 95th-percentile differences between finite-segment and continuous "
                "low-pass filtering in the no-FORCe controls, relative to the reference voltage range. "
                "Bottom: the actual 20 Hz low-pass response to an injected voltage step or one-sample "
                "spike, showing how a sharp disturbance can spread into nearby samples."
            ),
            "boundary_distributions": (
                "Distributions of adjacent-sample jumps at the −0.5 and +0.5 s cleaning joins, "
                "for Cz and FCz across matched pilot trials. Jumps are expressed as a percentage "
                "of each trial's BP no-FORCe reference voltage range. Curves farther right indicate "
                "larger jumps; the four lines compare the processing conditions."
            ),
            "actual_cleaning_residuals": (
                "FORCe-minus-control waveforms for two pilot trials selected near the median and "
                "95th percentile of the BP FORCe Cz jump at +0.5 s. Cz and FCz panels compare "
                "BP and split-filter cleaning changes relative to the reference voltage range. "
                "These residuals measure processing changes, not independently identified artifacts."
            ),
        },
        "tables": [
            (
                "Matched ERP processing changes",
                result_path("PRE_09") / "matched_erp/comparison_summary.csv",
            ),
            (
                "Output quality-screen summary",
                result_path("PRE_09") / "quality/final_quality_summary.csv",
            ),
            (
                "Boundary comparison",
                result_path("PRE_07") / "paired_boundary_summary.csv",
            ),
        ],
        "figures": [
            result_path("PRE_07") / "figures/filtering_effects.png",
            result_path("PRE_07") / "figures/boundary_distributions.png",
            result_path("PRE_07") / "figures/actual_cleaning_residuals.png",
        ],
    },
    "FEA_features_repeatability": {
        "title": "Features and within-participant repeatability",
        "summary": "The matched pilot audits sample-wise amplitudes, 100 ms means and channel sets. Central channels showed promising descriptive separation; decoder comparisons were needed to select a feature design. Repeatability varied by session and run.",
        "pdf": "Feature_audit_matched_processing_pilot_revised.pdf",
        "tables": [
            (
                "Time-point feature summary",
                result_path("FEA_01") / "set_timepoint_summary.csv",
            ),
            (
                "Repeatability summary",
                result_path("FEA_01") / "repeatability_summary.csv",
            ),
        ],
        "figures": sorted((result_path("FEA_01") / "figures").glob("*.png")),
    },
    erp_web_report.CATEGORY: erp_web_report.report_spec(),
    "DEC_decoding": {
        "title": "Displaced/non-displaced classification",
        "summary": "The fixed all-eight-channel 100 ms shrinkage LDA achieved 76.3% mean participant-level balanced accuracy in the 23 non-pilot participants. The model is trained within participant/session with held-out runs. Above-chance permutation inference remains pending; discrimination does not establish ErrP identity.",
        "pdf": "D_ND_classification_research_note.pdf",
        "figure_descriptions": {
            "permutation_LDA_primary": "Observed balanced accuracy and the participant-specific 95th-percentile permutation threshold for eight-channel LDA in the 23 non-pilot participants. Thresholds are unadjusted, not confidence intervals; use the participant table's Holm-adjusted p-values for corrected significance."
        },
        "tables": [
            (
                "Full-cohort model comparison",
                result_path("DEC_02") / "cohort_summary.csv",
            ),
            ("Participant results", result_path("DEC_02") / "participant_metrics.csv"),
            ("Session results", result_path("DEC_02") / "session_metrics.csv"),
            (
                "Graz-style tree comparison",
                result_path("DEC_03") / "cohort_summary.csv",
            ),
            (
                "Participant permutation significance",
                result_path("DEC_04") / "participant_significance.csv",
            ),
            (
                "Session permutation checks (uncorrected)",
                result_path("DEC_04") / "session_significance.csv",
            ),
            (
                "Permutation significance summary",
                result_path("DEC_04") / "cohort_summary.csv",
            ),
        ],
        "figures": [
            ROOT / "output/DEC_decoding/report/figures/participant_scores.png",
            ROOT / "output/DEC_decoding/report/figures/session_scores.png",
            ROOT / "output/DEC_decoding/report/figures/graz_comparison.png",
            ROOT / "output/DEC_decoding/report/figures/permutation_LDA_primary.png",
        ],
    },
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def waveform_data():
    """Read aggregate cohort/pilot means exported from the saved trial selections."""
    source = ROOT / "output/PRE_preprocessing_artifacts/report/waveform_means.json"
    if not source.exists():
        raise FileNotFoundError(
            "Run Code/helpers/export_report_waveforms.m in MATLAB before building PRE."
        )
    payload = json.loads(source.read_text(encoding="utf-8"))
    data = {}
    for record in payload["records"]:
        key = "|".join(
            str(record[k]) for k in ["subject", "session", "condition", "selection"]
        )
        assert key not in data
        for name in ["correct", "error"]:
            assert not record[name] or (
                len(record[name]) == 1000 and all(len(row) == 8 for row in record[name])
            )
        data[key] = record
    return data


STYLE = """
:root{font-family:system-ui,sans-serif;color:#20334b;background:#f3f6fa;line-height:1.55}
body{max-width:1280px;margin:auto;padding:24px}h1,h2{line-height:1.2}h1{font-size:2.1rem}
nav{display:flex;gap:18px;flex-wrap:wrap}a{color:#075da8}section,.card{background:white;border:1px solid #d8e1eb;border-radius:10px;padding:20px;margin:18px 0}
.controls{display:flex;flex-wrap:wrap;align-items:end;gap:14px;margin:16px 0}label{display:flex;flex-direction:column;font-weight:600;font-size:.9rem}select,input,button{font:inherit;padding:7px;border:1px solid #a6b5c6;border-radius:5px;max-width:100%}
[hidden]{display:none!important}.note{color:#53657a}.badge{background:#edf2f9;padding:3px 8px;border-radius:5px}img{max-width:100%;height:auto}figure{margin:10px 0}figcaption{font-size:.9rem;color:#53657a}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.chart{border:1px solid #d8e1eb;background:white;padding:8px;border-radius:6px}.chart canvas{width:100%;height:225px}
.tablewrap{overflow:auto;max-height:580px}table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid #e0e6ef;white-space:nowrap}th{background:#edf2f9;position:sticky;top:0}summary{cursor:pointer;font-weight:600}footer{font-size:.85rem;color:#53657a}@media(max-width:700px){body{padding:12px}.grid{grid-template-columns:1fr}}@media print{select,input,button,.controls{display:none}section{break-inside:avoid}}
"""
SCRIPT = r"""
const D=JSON.parse(document.getElementById('report-data').textContent);
const byId=id=>document.getElementById(id);
function option(select,values,all=true){if(all)select.add(new Option('All',''));values.forEach(v=>select.add(new Option(v,v)));}
function cell(v){const td=document.createElement('td');td.textContent=(typeof v==='string' && /^-?\d+\.\d+(e[-+]?\d+)?$/i.test(v))?Number(v).toPrecision(5):String(v??'');return td;}
// Each section owns its filters. Saved-image scope is explicit metadata.
const figureSubjects=[...new Set(D.figures.map(f=>f.subject).filter(Boolean))].sort();
const figureSessions=['pre','post','retest'].filter(ss=>D.figures.some(f=>f.session===ss));
option(byId('subject'),figureSubjects);option(byId('session'),figureSessions);
byId('figureSubjectField').hidden=figureSubjects.length===0;
byId('figureSessionField').hidden=figureSessions.length===0;
byId('figureScope').textContent=figureSubjects.length||figureSessions.length
    ?'These filters apply only to saved figures. Summary images without participant/session detail appear when the corresponding filter is All.'
    :(D.category.startsWith('PRE')?'These figures come from the two-participant pilot analysis. Each image has a fixed scope, described below; participant/session selections in other sections do not change it.':'These are fixed summary figures spanning participants or sessions. Choose a figure below; table selections do not change these images.');
function showFigure(){
    const f=D.figures.find(f=>f.name===byId('figure').value);
    byId('plot').hidden=!f;
    byId('figureDescription').textContent=f?.description||'';
    byId('figureDescription').hidden=!f?.description;
    if(f){byId('plot').src=f.src;byId('plot').alt=f.title;byId('plotcaption').textContent=f.title;}
    else{byId('plot').removeAttribute('src');byId('plotcaption').textContent='No saved figure matches these filters.';}
}
function renderGallery(){
    const previous=D.figures.find(f=>f.name===byId('figure').value);
    const available=D.figures.filter(f=>(!byId('subject').value||f.subject===byId('subject').value)&&(!byId('session').value||f.session===byId('session').value));
    const select=byId('figure');select.replaceChildren();
    available.forEach(f=>select.add(new Option(f.title,f.name)));
    if(previous){
        const keep=available.find(f=>f.name===previous.name)
            ||available.find(f=>f.kind===previous.kind&&f.session===previous.session)
            ||available.find(f=>f.kind===previous.kind);
        if(keep)select.value=keep.name;
    }
    showFigure();
}
byId('figure').onchange=showFigure;
['subject','session'].forEach(id=>byId(id).onchange=renderGallery);
const tableFilterLabels={subject:'Participant',session:'Session',sessionA:'Session A',sessionB:'Session B',level:'Summary level',cohort:'Cohort',family:'Inference family',significant_holm_05:'Holm significance (0/1)',model_id:'Model',condition:'Condition',referenceCondition:'Reference condition',channel:'Channel',channelSet:'Channel set',waveform:'Waveform',trialClass:'Trial class',alignment:'Alignment',component_window:'Component window',boundary:'Boundary (s)',contrast:'Contrast',test:'Test',resolution:'Resolution'};
const tableSelections=new Map();
function filterLabel(field,value){
    if(field==='condition'||field==='referenceCondition')return `${value} · ${conditionNames[value]||value}`;
    if(field==='subject'&&['ALL','Pooled'].includes(value))return value+' · pooled participants';
    if(['session','sessionA','sessionB'].includes(field)&&value==='ALL')return 'ALL · pooled sessions';
    return value;
}
function updateTableFilters(){
    const table=D.tables[byId('table').value],saved=tableSelections.get(table.title)||{};
    const holder=byId('tableFilters');holder.replaceChildren();
    for(const [field,title] of Object.entries(tableFilterLabels)){
        const values=[...new Set(table.rows.map(r=>r[field]).filter(v=>v!==undefined&&v!==''))].sort();
        if(!values.length)continue;
        const label=document.createElement('label');label.textContent=title;
        const select=document.createElement('select');select.dataset.field=field;
        select.setAttribute('aria-label','Summary '+title);select.add(new Option('All',''));
        values.forEach(v=>select.add(new Option(filterLabel(field,v),v)));
        if(values.includes(saved[field]))select.value=saved[field];
        select.onchange=()=>{
            const state={};holder.querySelectorAll('select').forEach(s=>state[s.dataset.field]=s.value);
            tableSelections.set(table.title,state);renderTable();
        };
        label.append(select);holder.append(label);
    }
    renderTable();
}
function renderTable(){
    const table=D.tables[byId('table').value];
    const filters=[...byId('tableFilters').querySelectorAll('select')];
    let rows=table.rows.filter(r=>filters.every(s=>!s.value||r[s.dataset.field]===s.value));
    const q=byId('search').value.toLowerCase();
    if(q)rows=rows.filter(r=>Object.values(r).join(' ').toLowerCase().includes(q));
    const headings=table.columns||Object.keys(table.rows[0]||{}),tr=document.createElement('tr');
    headings.forEach(h=>{const th=document.createElement('th');th.textContent=(table.labels||{})[h]||h;tr.append(th)});
    byId('tablehead').replaceChildren(tr);const body=byId('tablebody');body.replaceChildren();
    rows.slice(0,500).forEach(r=>{const row=document.createElement('tr');headings.forEach(h=>row.append(cell(r[h])));body.append(row)});
    const scope=!headings.includes('session')&&!headings.includes('sessionA')?' This table aggregates sessions.':'';
    byId('tablecount').textContent=`${rows.length} of ${table.rows.length} rows${rows.length>500?'; displaying first 500':''}.${scope} Filters apply only to this numerical table. No new tests are computed here.`;
}
D.tables.forEach((t,i)=>byId('table').add(new Option(t.title,i)));
byId('table').onchange=updateTableFilters;byId('search').oninput=renderTable;
// Waveforms use saved means only; all trial matching is performed in MATLAB.
const conditionNames={'1':'BP no-FORCe','2':'BP FORCe','3':'Split no-FORCe','4':'Split FORCe'};
function waveRecord(subject,session,condition,selection){
    return D.waves[[subject,session,condition,selection].join('|')];
}
function channelCurves(record,ch){
    if(!record)return [[],[],[]];
    const correct=record.correct.map(row=>row[ch]);
    const error=record.error.map(row=>row[ch]);
    return [correct,error,correct.length&&error.length?error.map((v,i)=>v-correct[i]):[]];
}
// Remember the user's pilot choices even while another participant cannot show them.
const waveChoice={condition:'1',selection:'all'};
function updateWaveControls(){
    const subject=byId('waveSubject').value;
    const available=new Set(Object.values(D.waves).filter(r=>r.subject===subject).map(r=>String(r.condition)));
    for(const opt of byId('condition').options)opt.disabled=!available.has(opt.value);
    byId('condition').value=available.has(waveChoice.condition)?waveChoice.condition:'1';
    const matched=Object.values(D.waves).some(r=>r.subject===subject&&r.selection==='matched');
    byId('selection').querySelector('[value="matched"]').disabled=!matched;
    byId('selection').value=matched?waveChoice.selection:'all';
    byId('overlay').disabled=byId('condition').value==='1';
    drawWaveforms();
}
function drawWaveforms(){
    if(!D.waves)return;
    const subject=byId('waveSubject').value,session=byId('waveSession').value;
    const condition=byId('condition').value,selection=byId('selection').value;
    const record=waveRecord(subject,session,condition,selection);
    const overlay=byId('overlay').checked&&!byId('overlay').disabled;
    const reference=overlay?waveRecord(subject,session,'1',selection):null;
    const pilot=['mle01','spe30'].includes(subject);
    const cleaning=['2','4'].includes(condition);
    const selectionText=selection==='matched'?'Matched trial IDs accepted by all four pilot conditions':'All trials accepted by this condition';
    byId('waveTitle').textContent=`${subject} / ${session} — ${conditionNames[condition]}`;
    byId('counts').textContent=record?`${selectionText}. Correct (ND) n=${record.nND}; Error (D) n=${record.nD}.`:'No saved accepted trials for this participant/session.';
    if(record&&(!record.nND||!record.nD))byId('counts').textContent+=' A class has no accepted trials; its mean and Error − Correct are unavailable.';
    const status=D.sessionStatus[subject+'|'+session];
    const reasons={fewer_than_two_accepted_recordings:'fewer than two accepted recordings',a_training_fold_has_only_one_class:'a training fold has only one class'};
    if(status&&status!=='ok')byId('counts').textContent+=' Limited data: this session was ineligible for classification ('+(reasons[status]||status)+').';
    if(reference)byId('counts').textContent+=` Dashed BP no-FORCe overlay: Correct n=${reference.nND}; Error n=${reference.nD}.`;
    byId('waveDetails').textContent=(pilot?'Other conditions are available for this pilot. Matched uses the four-condition intersection; all accepted may use different trial sets across conditions. ':'Only the primary BP no-FORCe condition is available here; other conditions and matching are limited to the two pilots. ')+(cleaning?'Dotted markers show FORCe joins at −0.5 and +0.5 s. ':'This condition has no FORCe cleaning joins. ')+ 'Movement onset is 0 s; baseline is [−0.2,0) s. Axes stay fixed across sessions, conditions and selections within each participant/channel. Blue: Correct; red: Error; black: Error − Correct.';
    byId('downloadWave').disabled=!record;
    byId('waves').replaceChildren();
    if(!record)return;
    D.channels.forEach((channel,ch)=>{
        const panel=document.createElement('div');panel.className='chart';
        const title=document.createElement('b');title.textContent=channel+' (µV)';
        const canvas=document.createElement('canvas');canvas.width=1000;canvas.height=450;
        canvas.setAttribute('aria-label',`${subject} ${session} ${channel} ${conditionNames[condition]} ${selection}`);
        panel.append(title,canvas);byId('waves').append(panel);
        const ctx=canvas.getContext('2d'),left=85,right=975,top=20,bottom=385;
        let extent=1;
        for(const r of Object.values(D.waves).filter(r=>r.subject===subject))
            for(const values of channelCurves(r,ch))for(const v of values)extent=Math.max(extent,Math.abs(v));
        extent*=1.08;
        const px=t=>left+(t+1)/2*(right-left),py=v=>bottom-(v+extent)/(2*extent)*(bottom-top);
        ctx.fillStyle='white';ctx.fillRect(0,0,1000,450);ctx.font='22px system-ui';
        for(const t of [-1,-.5,0,.5,1]){
            ctx.strokeStyle=t===0?'#596778':'#d4dce6';ctx.setLineDash([]);
            ctx.beginPath();ctx.moveTo(px(t),top);ctx.lineTo(px(t),bottom);ctx.stroke();
            ctx.fillStyle='#53657a';ctx.fillText(t.toFixed(1),px(t)-15,bottom+30);
        }
        if(cleaning){
            ctx.strokeStyle='#6c7580';ctx.setLineDash([4,6]);
            for(const t of [-.5,.5]){ctx.beginPath();ctx.moveTo(px(t),top);ctx.lineTo(px(t),bottom);ctx.stroke();}
        }
        ctx.setLineDash([]);ctx.fillText('Time from movement (s)',340,440);
        for(const v of [-extent,0,extent])ctx.fillText(v.toFixed(1),5,py(v)+7);
        ctx.strokeStyle='#8897a8';ctx.beginPath();ctx.moveTo(left,py(0));ctx.lineTo(right,py(0));ctx.stroke();
        function trace(r,dashed){
            channelCurves(r,ch).forEach((values,i)=>{
                ctx.strokeStyle=['#1468b3','#ce3838','#222'][i];ctx.lineWidth=dashed?2:3;
                ctx.setLineDash(dashed?[9,7]:[]);ctx.beginPath();
                values.forEach((v,j)=>{const x=px(-1+j*.002),y=py(v);if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();
            });ctx.setLineDash([]);
        }
        if(reference)trace(reference,true);trace(record,false);
    });
}
function downloadWaveforms(){
    const canvas=document.createElement('canvas');canvas.width=2080;canvas.height=2240;
    const ctx=canvas.getContext('2d');ctx.fillStyle='white';ctx.fillRect(0,0,canvas.width,canvas.height);
    ctx.fillStyle='#20334b';ctx.font='bold 34px system-ui';ctx.fillText(byId('waveTitle').textContent,35,50);
    ctx.font='23px system-ui';
    const text=byId('counts').textContent+' Blue: Correct; red: Error; black: Error − Correct.';
    let line='',y=90;
    for(const word of text.split(' ')){
        if(ctx.measureText(line+word).width>1980){ctx.fillText(line,35,y);line='';y+=30;}
        line+=word+' ';
    }
    ctx.fillText(line,35,y);ctx.fillText('Movement onset: 0 s. Baseline: [−0.2,0) s. Fixed axes across sessions for each channel.'+(['2','4'].includes(byId('condition').value)?' Dotted: FORCe joins at ±0.5 s.':''),35,y+35);
    document.querySelectorAll('#waves canvas').forEach((source,i)=>{
        const x=35+(i%2)*1030,top=230+Math.floor(i/2)*500;
        ctx.font='bold 27px system-ui';ctx.fillText(D.channels[i]+' (µV)',x,top);ctx.drawImage(source,x,top+10);
    });
    canvas.toBlob(blob=>{
        const link=document.createElement('a');link.href=URL.createObjectURL(blob);
        link.download=[byId('waveSubject').value,byId('waveSession').value,'condition'+byId('condition').value,byId('selection').value].join('_')+'.png';
        link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
    });
}
if(D.waves){
    byId('waveSection').hidden=false;
    option(byId('waveSubject'),[...new Set(Object.values(D.waves).map(r=>r.subject))].sort(),false);
    option(byId('waveSession'),['pre','post','retest'],false);
    ['waveSubject','waveSession','overlay'].forEach(id=>byId(id).onchange=updateWaveControls);
    ['condition','selection'].forEach(id=>byId(id).onchange=()=>{waveChoice[id]=byId(id).value;updateWaveControls();});
    byId('downloadWave').onclick=downloadWaveforms;updateWaveControls();
}
updateTableFilters();renderGallery();
if(location.hostname==='htmlpreview.github.io'){const base='https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/'+D.category+'/report/index.html';document.querySelectorAll('a[href]').forEach(a=>{const u=new URL(a.getAttribute('href'),base);a.href=u.pathname.endsWith('/index.html')?'https://htmlpreview.github.io/?'+u.href:(u.pathname.endsWith('/')?u.href.replace('/blob/main/','/tree/main/'):u.href);});}
"""


def build(category, spec):
    related = " · ".join(
        f'<a href="../../{c}/report/index.html">{v["title"]}</a>'
        for c, v in REPORTS.items()
        if c != category
    )
    if category == audit_web_report.CATEGORY:
        audit_web_report.build(STYLE, related)
        return
    destination = ROOT / "output" / category / "report"
    destination.mkdir(parents=True, exist_ok=True)
    erp = category == erp_web_report.CATEGORY
    tables = [
        {"title": title, "rows": read_csv(path)}
        for title, path in spec["tables"]
        if path.exists()
    ]
    for table in tables:
        if table["title"] == "Participant permutation significance":
            table["columns"] = [
                "subject",
                "cohort",
                "model_id",
                "balanced_accuracy",
                "chance_95",
                "p_value",
                "p_holm",
            ]
        elif table["title"] == "Session permutation checks (uncorrected)":
            table["columns"] = [
                "subject",
                "session",
                "cohort",
                "model_id",
                "n_trials",
                "balanced_accuracy",
                "chance_95",
                "p_value",
            ]
        if "columns" in table:
            table["labels"] = {
                "subject": "Participant",
                "session": "Session",
                "cohort": "Cohort",
                "model_id": "Model",
                "n_trials": "Trials",
                "balanced_accuracy": "Balanced accuracy",
                "chance_95": "95% chance threshold",
                "p_value": "p",
                "p_holm": "Holm-adjusted p",
            }
    if erp:
        for table in tables:
            table["labels"] = erp_web_report.TABLE_LABELS
    figure_subjects = {
        row["subject"]
        for table in tables
        for row in table["rows"]
        if row.get("subject") not in (None, "", "ALL", "Pooled")
    }
    figures = [
        {
            "name": p.stem,
            "title": spec.get("figure_titles", {}).get(p.stem, p.stem.replace("_", " ")),
            "description": spec.get("figure_descriptions", {}).get(p.stem, ""),
            "subject": next(
                (v for v in sorted(figure_subjects) if v in p.stem.split("_")), None
            ),
            "session": next(
                (v for v in ("pre", "post", "retest") if v in p.stem.split("_")), None
            ),
            "kind": "_".join(
                v
                for v in p.stem.split("_")
                if v not in figure_subjects and v not in ("pre", "post", "retest")
            ),
            "src": "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode(),
        }
        for p in spec["figures"]
        if p.exists()
    ]
    data = {
        "category": category,
        "tables": tables,
        "figures": figures,
        "subjects": sorted(
            {
                row["subject"]
                for table in tables
                for row in table["rows"]
                if row.get("subject")
            }
        ),
        "channels": ["P3", "PO3", "PO7", "CP5", "CP1", "Cz", "FCz", "FC1"],
    }
    if category.startswith("PRE"):
        data["waves"] = waveform_data()
        data["subjects"] = sorted({r["subject"] for r in data["waves"].values()})
        data["sessionStatus"] = {
            row["subject"] + "|" + row["session"]: row["status"]
            for row in read_csv(result_path("DEC_02") / "session_eligibility.csv")
        }
    if erp:
        data["erpGalleryWindows"] = erp_web_report.gallery_windows()
        data["erpDistancePlots"] = {}
        for selection in ("hit_detected", "no_hit_detected"):
            plot = result_path("ERP_02") / f"distance_associations_{selection}.png"
            if plot.is_file():
                data["erpDistancePlots"][selection] = "data:image/png;base64," + base64.b64encode(plot.read_bytes()).decode()
        data["erp"] = json.loads(
            (result_path("ERP_01") / "waveform_means.json").read_text(encoding="utf-8")
        )
        steering_means = result_path("ERP_02") / "waveform_means.json"
        if steering_means.exists():
            data["erpSteering"] = json.loads(steering_means.read_text(encoding="utf-8"))
        trajectory_means = result_path("ERP_03") / "waveform_means.json"
        if trajectory_means.exists():
            data["erpTrajectories"] = json.loads(trajectory_means.read_text(encoding="utf-8"))
        outcome_means = result_path("ERP_04") / "waveform_means.json"
        if outcome_means.exists():
            data["erpOutcomes"] = json.loads(outcome_means.read_text(encoding="utf-8"))
    experiments = []
    for eid, e in EXPERIMENTS.items():
        if category not in e["result"]:
            continue
        local = "../../../" + e["workflow"]
        experiments.append(
            f'<li><b>{eid}</b> · <a href="{local}">workflow and scripts</a> · <a href="../{Path(e["result"]).name}/">results</a></li>'
        )
    summary = html.escape(spec["summary"])
    if category.startswith("PRE"):
        phrase = "Four-condition comparisons remain limited to mle01 and spe30"
        summary = summary.replace(
            phrase, "<strong>" + phrase + " (pilot only)</strong>"
        )
    if (
        category.startswith("DEC")
        and (result_path("DEC_04") / "participant_significance.csv").exists()
    ):
        inference_rows = read_csv(
            result_path("DEC_04") / "participant_significance.csv"
        )
        primary = [r for r in inference_rows if r["family"] == "primary_validation"]
        significant = sum(r["significant_holm_05"] == "1" for r in primary)
        summary = summary.replace(
            "Above-chance permutation inference remains pending; discrimination does not establish ErrP identity.",
            f"Permutation tests support above-null LDA performance after Holm correction in {significant}/{len(primary)} non-pilot participants. Discrimination does not establish ErrP identity.",
        )
    table_scope = (
        '<p class="note"><strong>Pilot only — mle01 and spe30.</strong> '
        "These numerical tables cover the pilot artifact-handling and boundary analyses, "
        "including pooled rows from those two participants. The waveform section above covers all 25 participants.</p>"
        if category.startswith("PRE")
        else ""
    )
    supplements = []
    if (
        category.startswith("PRE")
        and (destination / "BP_noFORCe_participant_waveforms.pdf").exists()
    ):
        supplements.append(
            '<a href="BP_noFORCe_participant_waveforms.pdf">All participant/session waveforms (PDF)</a>'
        )
    if (
        category.startswith("DEC")
        and (destination / "D_ND_permutation_significance_note.pdf").exists()
    ):
        supplements.append(
            '<a href="D_ND_permutation_significance_note.pdf">Primary LDA permutation note (PDF)</a>'
        )
    supplement_links = "".join(" · " + link for link in supplements)
    inference_scope = ""
    if (
        category.startswith("DEC")
        and (result_path("DEC_04") / "participant_significance.csv").exists()
    ):
        inference_scope = (
            "<p><strong>Permutation inference:</strong> choose the participant significance table below for observed balanced accuracy, "
            "the unadjusted 95th-percentile chance threshold, and raw/Holm p-values for the four fixed classifiers. "
            "Scores are fractions (0–1). Primary LDA: 23 non-pilot tests; secondary models: a separate 69-test family; "
            "the eight pilot/model tests are exploratory. Session-table p-values are uncorrected exploratory checks.</p>"
            "<details><summary>Permutation method and interpretation</summary><p>1,999 shuffles preserve D/ND counts within each recording. "
            "Every permutation refits the models on the same whole-recording holdouts, including training-fold top-100 feature selection. "
            "Session balanced accuracy pools test predictions; participant scores average eligible sessions equally. "
            "One-sided p=(exceedances+1)/2000, with minimum 0.0005; Holm adjusts within the stated families. "
            "The 95th-percentile threshold is unadjusted; use adjusted p-values for corrected significance. "
            "Labels must be exchangeable within recordings. Discrimination does not establish ErrP identity.</p>"
            '<p>Methods: <a href="https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.permutation_test_score.html">grouped permutation testing</a>; '
            '<a href="https://doi.org/10.2202/1544-6115.1585">Monte Carlo p-values</a>.</p></details>'
        )
    scope = (
        erp_web_report.SCOPE if erp else
        "This report displays saved numerical results and condition means. It does not rerun preprocessing, alter trial selection or fit a classifier. Displayed waveform values are rounded to five decimal places in µV. Raw recordings, individual trials and fitted models are excluded."
    )
    method_note = (
        "The browser displays aggregate means at the original 2 ms spacing, rounded to 0.01 µV before aggregation. The group tests use full precision. See the workflow for test windows and matching details."
        if erp else
        "Input flags indicate suspected contamination; they do not identify EOG/EMG sources definitively. Classifier differences do not establish an ErrP. Full methods, processing contrasts and limitations are in the PDF and experiment READMEs."
    )
    pdf = f'<a href="{spec["pdf"]}">Formal PDF note</a> · ' if spec.get("pdf") else ""
    erp_nav = erp_web_report.FINDINGS_NAV if erp else ""
    gallery_window = erp_web_report.GALLERY_WINDOW if erp else ""
    gallery_notes = erp_web_report.GALLERY_NOTES if erp else ""
    erp_style = erp_web_report.STYLE if erp else ""
    erp_script = ""
    erp_gallery = ""
    repeatability = ""
    if erp:
        erp_gallery = '<div id="erpFilteredFigure" hidden></div>'
        erp_script = "\n".join(Path(__file__).with_name(name).read_text(encoding="utf-8")
                               for name in ("erp_waveforms.js", "erp_figure_gallery.js", "erp_findings.js"))
        table_scope = erp_web_report.TEST_SCOPE
        if any(table["title"] == "Recording amplitudes" for table in tables):
            repeatability = erp_web_report.REPEATABILITY_SECTION
            erp_script += Path(__file__).with_name("erp_repeatability.js").read_text(encoding="utf-8")
    gallery_controls = f'''<p id="figureScope" class="note"></p><div class="controls"><label id="figureSubjectField">Participant<select id="subject"></select></label><label id="figureSessionField">Session<select id="session"></select></label><label>Figure<select id="figure"></select></label>{gallery_window}</div><p id="figureDescription" class="note" aria-live="polite"></p>{gallery_notes}<figure><img id="plot" alt="Saved analysis figure">{erp_gallery}<figcaption id="plotcaption"></figcaption></figure>'''
    numerical_tables = f'''{table_scope}{inference_scope}<p class="note">Choose a table, then use its own filters below. These selections do not change the waveforms or saved figures.</p><div class="controls"><label>Table<select id="table"></select></label><label>Search rows<input id="search" placeholder="Search this table"></label></div><div id="tableFilters" class="controls"></div><p id="tablecount" class="note"></p><div class="tablewrap"><table><thead id="tablehead"></thead><tbody id="tablebody"></tbody></table></div>'''
    method_links = f"<ul>{''.join(experiments)}</ul><p>{method_note}</p>"
    if erp:
        report_sections = (
            erp_web_report.WAVE_SECTION.format(gallery=gallery_controls)
            + erp_web_report.FINDINGS_SECTION
            + f'<details id="erp-methods"><summary>Methods and detailed results</summary>'
              f'<p>{scope}</p>{method_links}{repeatability}<section><h3>Numerical tables</h3>'
              f'{numerical_tables}</section></details>'
        )
        gallery_section = table_section = ""
    else:
        report_sections = (
            f'<section><h2>Scope and interpretation</h2><p>{scope}</p>'
            f'<details><summary>Methods and experiment navigation</summary>{method_links}</details></section>'
        )
        gallery_section = f'<section id="savedFigures"><h2>Saved figures</h2>{gallery_controls}</section>'
        table_section = f'<section><h2>Numerical summaries</h2>{numerical_tables}</section>'
    body = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(spec['title'])}</title><style>{STYLE}{erp_style}</style></head><body>
<nav aria-label="Research reports">{related}</nav><h1>{html.escape(spec['title'])}</h1><p>{summary}</p>
<p>{pdf}<a href="../../../EXPERIMENTS.md">Experiment registry</a>{supplement_links}</p>
{erp_nav}
{report_sections}
<section id="waveSection" hidden><h2>Participant/session eight-channel waveforms</h2><div class="controls"><label>Participant<select id="waveSubject"></select></label><label>Session<select id="waveSession"></select></label><label>Processing condition<select id="condition"><option value="1">1 · BP no-FORCe</option><option value="2">2 · BP FORCe (pilot only)</option><option value="3">3 · Split no-FORCe (pilot only)</option><option value="4">4 · Split FORCe (pilot only)</option></select></label><label>Trial selection<select id="selection"><option value="all">All accepted trials</option><option value="matched">Matched across four conditions (pilot only)</option></select></label><label>Overlay BP no-FORCe<input type="checkbox" id="overlay"></label><button id="downloadWave" type="button">Download figure (PNG)</button></div><h3 id="waveTitle"></h3><p id="counts" class="note"></p><p id="waveDetails" class="note"></p><p class="note">The cohort view uses accepted decoder-analysis trial IDs, including sessions ineligible for cross-validation, with quality eligibility across the complete three-second interval. Pilot conditions use that same interval; matching does not balance the two class counts. The historical two-second FORCe cohort run is separate and is not included here.</p><div id="waves" class="grid"></div></section>
{gallery_section}
{table_section}
<footer>Generated from existing aggregate outputs by Code/helpers/build_web_reports.py. HTML reports are portable; linked code/PDF files require their surrounding repository layout. Report controls display saved results and do not rerun analyses.</footer>
<script id="report-data" type="application/json">{json.dumps(data,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')}</script><script>{SCRIPT}{erp_script}</script></body></html>'''
    (destination / "index.html").write_text(body, encoding="utf-8")
    print(
        f'{category}: {len(figures)} figures; {sum(len(t["rows"]) for t in tables)} summary rows; {len(body)/1e6:.1f} MB HTML'
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--category", choices=REPORTS, help="Build only this category")
    args = parser.parse_args()
    for category, spec in REPORTS.items():
        if args.category is None or category == args.category:
            build(category, spec)
