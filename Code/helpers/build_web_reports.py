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

REPORTS = {
    "PRE_preprocessing_artifacts": {
        "title": "Preprocessing and artifact handling",
        "summary": "The two-participant checks support a no-FORCe working analysis with targeted quality review and FORCe as a secondary comparison. Sharp-join attenuation alone does not demonstrate neural-signal preservation.",
        "pdf": "FORCe_retention_and_ErrP_pilot_note.pdf",
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
    "DEC_decoding": {
        "title": "Displaced/non-displaced classification",
        "summary": "The fixed all-eight-channel 100 ms shrinkage LDA achieved 76.3% mean participant-level balanced accuracy in the 23 non-pilot participants. The model is trained within participant/session with held-out runs. Above-chance permutation inference remains pending; discrimination does not establish ErrP identity.",
        "pdf": "D_ND_classification_research_note.pdf",
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
        ],
        "figures": [
            ROOT / "output/DEC_decoding/report/figures/participant_scores.png",
            ROOT / "output/DEC_decoding/report/figures/session_scores.png",
            ROOT / "output/DEC_decoding/report/figures/graz_comparison.png",
        ],
    },
}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def waveform_data():
    """Only saved condition means; no individual EEG trials are embedded."""
    source = result_path("PRE_09") / "matched_erp/matched_waveforms.csv"
    data = {}
    for row in read_csv(source):
        key = "|".join(
            row[k] for k in ["subject", "session", "channel", "condition", "waveform"]
        )
        if key not in data:
            data[key] = {
                "values": [],
                "nND": int(row["nonDisplaced"]),
                "nD": int(row["displaced"]),
            }
        data[key]["values"].append(round(float(row["meanUV"]), 5))
    assert len(data) == 2 * 3 * 8 * 4 * 3
    assert all(len(v["values"]) == 1000 for v in data.values())
    return data


STYLE = """
:root{font-family:system-ui,sans-serif;color:#20334b;background:#f3f6fa;line-height:1.55}
body{max-width:1280px;margin:auto;padding:24px}h1,h2{line-height:1.2}h1{font-size:2.1rem}
nav{display:flex;gap:18px;flex-wrap:wrap}a{color:#075da8}section,.card{background:white;border:1px solid #d8e1eb;border-radius:10px;padding:20px;margin:18px 0}
.controls{display:flex;flex-wrap:wrap;align-items:end;gap:14px;margin:16px 0}label{display:flex;flex-direction:column;font-weight:600;font-size:.9rem}select,input{font:inherit;padding:7px;border:1px solid #a6b5c6;border-radius:5px;max-width:100%}
.note{color:#53657a}.badge{background:#edf2f9;padding:3px 8px;border-radius:5px}img{max-width:100%;height:auto}figure{margin:10px 0}figcaption{font-size:.9rem;color:#53657a}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.chart{border:1px solid #d8e1eb;background:white;padding:8px;border-radius:6px}.chart canvas{width:100%;height:225px}
.tablewrap{overflow:auto;max-height:580px}table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{text-align:left;padding:7px 10px;border-bottom:1px solid #e0e6ef;white-space:nowrap}th{background:#edf2f9;position:sticky;top:0}summary{cursor:pointer;font-weight:600}footer{font-size:.85rem;color:#53657a}@media(max-width:700px){body{padding:12px}.grid{grid-template-columns:1fr}}@media print{select,input,.controls{display:none}section{break-inside:avoid}}
"""
SCRIPT = r"""
const D=JSON.parse(document.getElementById('report-data').textContent);
const byId=id=>document.getElementById(id);
function option(select,values,all=true){if(all)select.add(new Option('All',''));values.forEach(v=>select.add(new Option(v,v)));}
function cell(v){const td=document.createElement('td');td.textContent=(typeof v==='string' && /^-?\d+\.\d+(e[-+]?\d+)?$/i.test(v))?Number(v).toPrecision(5):String(v??'');return td;}
option(byId('subject'),D.subjects);option(byId('session'),['pre','post','retest']);
function filtered(rows){return rows.filter(r=>(!byId('subject').value||!r.subject||r.subject===byId('subject').value)&&(!byId('session').value||!r.session||r.session===byId('session').value));}
function renderTable(){const table=D.tables[byId('table').value];let rows=filtered(table.rows);const q=byId('search').value.toLowerCase();if(q)rows=rows.filter(r=>Object.values(r).join(' ').toLowerCase().includes(q));const node=byId('tablebody');node.replaceChildren();const headings=Object.keys(table.rows[0]||{});const tr=document.createElement('tr');headings.forEach(h=>{const th=document.createElement('th');th.textContent=h;tr.append(th)});byId('tablehead').replaceChildren(tr);rows.slice(0,500).forEach(r=>{const row=document.createElement('tr');headings.forEach(h=>row.append(cell(r[h])));node.append(row)});byId('tablecount').textContent=`${rows.length} matching rows${rows.length>500?'; displaying first 500':''}. Values are saved estimates; rows without a session field summarise across sessions. No new tests are computed here.`;}
function renderGallery(){const available=D.figures.filter(f=>(!byId('subject').value||!D.subjects.some(s=>f.name.includes(s))||f.name.includes(byId('subject').value))&&(!byId('session').value||!['pre','post','retest'].some(s=>f.name.includes('_'+s+'_'))||f.name.includes('_'+byId('session').value+'_')));const select=byId('figure');select.replaceChildren();available.forEach((f,i)=>select.add(new Option(f.name,i)));const show=()=>{const f=available[select.value];byId('plot').hidden=!f;if(f){byId('plot').src=f.src;byId('plot').alt=f.name;byId('plotcaption').textContent=f.name;}};select.onchange=show;show();}
D.tables.forEach((t,i)=>byId('table').add(new Option(t.title,i)));byId('table').onchange=renderTable;byId('search').oninput=renderTable;
function drawWaveforms(){if(!D.waves)return;const subject=byId('waveSubject').value,session=byId('waveSession').value,condition=byId('condition').value;const waveNames=['Correct_ND','Error_D','Error_minus_Correct'];const colors=['#1468b3','#ce3838','#222'];let counts=null;byId('waves').replaceChildren();D.channels.forEach(channel=>{const panel=document.createElement('div');panel.className='chart';const title=document.createElement('b');title.textContent=channel+' (µV)';const canvas=document.createElement('canvas');canvas.width=1000;canvas.height=450;canvas.setAttribute('aria-label',`${subject} ${session} ${channel} condition ${condition}`);panel.append(title,canvas);byId('waves').append(panel);const ctx=canvas.getContext('2d'),left=85,right=975,top=20,bottom=385;let extent=1;for(const ss of ['pre','post','retest'])for(const cc of ['1','2','3','4'])for(const wave of waveNames){const d=D.waves[[subject,ss,channel,cc,wave].join('|')];if(d)for(const v of d.values)extent=Math.max(extent,Math.abs(v));}extent*=1.08;const px=t=>left+(t+1)/2*(right-left),py=v=>bottom-(v+extent)/(2*extent)*(bottom-top);ctx.font='22px system-ui';ctx.strokeStyle='#d4dce6';for(const t of [-1,-.5,0,.5,1]){ctx.beginPath();ctx.moveTo(px(t),top);ctx.lineTo(px(t),bottom);ctx.stroke();ctx.fillStyle='#53657a';ctx.fillText(t.toFixed(1),px(t)-15,bottom+30);}ctx.fillText('Time from movement (s)',340,440);for(const v of [-extent,0,extent]){ctx.fillText(v.toFixed(1),5,py(v)+7);}ctx.strokeStyle='#8897a8';ctx.beginPath();ctx.moveTo(left,py(0));ctx.lineTo(right,py(0));ctx.stroke();function trace(cc,dashed){waveNames.forEach((wave,i)=>{const d=D.waves[[subject,session,channel,cc,wave].join('|')];if(!d)return;counts=d;ctx.strokeStyle=colors[i];ctx.lineWidth=dashed?2:3;ctx.setLineDash(dashed?[9,7]:[]);ctx.beginPath();d.values.forEach((v,j)=>{const x=px(-1+j*.002),y=py(v);if(j===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);});ctx.stroke();});}if(byId('overlay').checked&&condition!=='1')trace('1',true);trace(condition,false);});byId('counts').textContent=counts?`${subject} / ${session}: Correct n=${counts.nND}; Error n=${counts.nD}. Matched trials across all four conditions. Blue: Correct; red: Error; black: Error − Correct. Dashed overlay: condition 1.`:'';}
if(D.waves){byId('waveSection').hidden=false;option(byId('waveSubject'),['mle01','spe30'],false);option(byId('waveSession'),['pre','post','retest'],false);['waveSubject','waveSession','condition','overlay'].forEach(id=>byId(id).onchange=drawWaveforms);drawWaveforms();}
['subject','session'].forEach(id=>byId(id).onchange=()=>{renderTable();renderGallery();});renderTable();renderGallery();
if(location.hostname==='htmlpreview.github.io'){const base='https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/'+D.category+'/report/index.html';document.querySelectorAll('a[href]').forEach(a=>{const u=new URL(a.getAttribute('href'),base);a.href=u.pathname.endsWith('/index.html')?'https://htmlpreview.github.io/?'+u.href:(u.pathname.endsWith('/')?u.href.replace('/blob/main/','/tree/main/'):u.href);});}
"""


def build(category, spec):
    destination = ROOT / "output" / category / "report"
    destination.mkdir(exist_ok=True)
    tables = [
        {"title": title, "rows": read_csv(path)}
        for title, path in spec["tables"]
        if path.exists()
    ]
    figures = [
        {
            "name": p.stem,
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
    experiments = []
    for eid, e in EXPERIMENTS.items():
        if category not in e["result"]:
            continue
        local = "../../../" + e["workflow"]
        experiments.append(
            f'<li><b>{eid}</b> · <a href="{local}">workflow and scripts</a> · <a href="../{Path(e["result"]).name}/">results</a></li>'
        )
    related = " · ".join(
        f'<a href="../../{c}/report/index.html">{v["title"]}</a>'
        for c, v in REPORTS.items()
        if c != category
    )
    body = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(spec['title'])}</title><style>{STYLE}</style></head><body>
<nav aria-label="Research reports">{related}</nav><h1>{html.escape(spec['title'])}</h1><p>{html.escape(spec['summary'])}</p>
<p><a href="{spec['pdf']}">Formal PDF note</a> · <a href="../../../EXPERIMENTS.md">Experiment registry</a></p>
<section><h2>Scope and interpretation</h2><p>This report displays saved numerical results and condition means. It does not rerun preprocessing, alter trial selection or fit a classifier. Displayed waveform values are rounded to five decimal places in µV. Raw recordings, individual trials and fitted models are excluded.</p><details><summary>Methods and experiment navigation</summary><ul>{''.join(experiments)}</ul><p>Input flags indicate suspected contamination; they do not identify EOG/EMG sources definitively. Classifier differences do not establish an ErrP. Full methods, processing contrasts and limitations are in the PDF and experiment READMEs.</p></details></section>
<section id="waveSection" hidden><h2>Matched eight-channel waveforms</h2><div class="controls"><label>Participant<select id="waveSubject"></select></label><label>Session<select id="waveSession"></select></label><label>Processing condition<select id="condition"><option value="1">1 · BP no-FORCe</option><option value="2">2 · BP FORCe</option><option value="3">3 · Split no-FORCe</option><option value="4">4 · Split FORCe</option></select></label><label>Overlay BP no-FORCe<input type="checkbox" id="overlay"></label></div><p id="counts" class="note"></p><p class="note">Axes are fixed across sessions/conditions within each participant and channel. Joins are at −0.5 and +0.5 s; movement onset is 0 s. Baseline: [−0.2,0) s.</p><div id="waves" class="grid"></div></section>
<section><h2>Saved figures</h2><p class="note">Overview figures can include multiple participants or sessions.</p><div class="controls"><label>Participant<select id="subject"></select></label><label>Session<select id="session"></select></label><label>Figure<select id="figure"></select></label></div><figure><img id="plot" alt="Saved analysis figure"><figcaption id="plotcaption"></figcaption></figure></section>
<section><h2>Numerical summaries</h2><div class="controls"><label>Table<select id="table"></select></label><label>Search rows<input id="search" placeholder="e.g. LDA_full or Cz"></label></div><p id="tablecount" class="note"></p><div class="tablewrap"><table><thead id="tablehead"></thead><tbody id="tablebody"></tbody></table></div></section><footer>Generated from existing aggregate outputs by Code/helpers/build_web_reports.py. HTML reports are portable; linked code/PDF files require their surrounding repository layout. No new significance tests are implied.</footer>
<script id="report-data" type="application/json">{json.dumps(data,separators=(',',':'),ensure_ascii=False).replace('</','<\\/')}</script><script>{SCRIPT}</script></body></html>'''
    (destination / "index.html").write_text(body, encoding="utf-8")
    print(
        f'{category}: {len(figures)} figures; {sum(len(t["rows"]) for t in tables)} summary rows; {len(body)/1e6:.1f} MB HTML'
    )


if __name__ == "__main__":
    for category, spec in REPORTS.items():
        build(category, spec)
