const D = JSON.parse(document.getElementById('audit-data').textContent);
const byId = id => document.getElementById(id);
const colors = {cursor:'#1864a4', jump:'#7543a6', end:'#087f67', steer:'#b05b16', hit:'#a41662', neutral:'#53657a'};
const sessions = ['pre', 'post', 'retest'];
const labels = {
    hit_detected:'Hit detected', no_hit_detected:'No hit detected', not_assessed:'Hit not assessed',
    unlinked:'Unlinked', not_applicable:'Not applicable',
    detected:'Detected', not_detected:'Not detected', above_at_window_start:'Above threshold at window start',
    early:'Early (confirmed by 250 ms)', late:'Later confirmation', incomplete:'Incomplete 250 ms window',
    endpoint_unavailable:'Endpoint unavailable', too_short:'Too short to assess',
};
const metricNames = {
    movement_eeg_ms_from_target:'EEG target to movement',
    movement_mouse_ms_from_target:'Mouse target to movement',
    movement_mouse_minus_eeg_ms:'Mouse minus EEG interval',
    jump_eeg_ms_from_movement:'EEG movement to jump',
    jump_mouse_ms_from_movement:'Mouse movement to jump',
    jump_mouse_minus_eeg_ms:'Mouse minus EEG interval',
};
const candidateNames = {
    forward_step_px:'Forward step (px per sample)', step_2d_px:'2D step (px per sample)',
    forward_speed_mm_s:'Forward speed (mm/s)', speed_2d_mm_s:'2D speed (mm/s)',
    forward_acceleration_mm_s2:'Forward acceleration (mm/s²)', forward_step_change_px:'Change in forward step (px)',
    forward_position_px:'Absolute forward position (px)', elapsed_from_movement_ms:'Time since movement onset (ms)',
    forward_3_px:'3 px forward step',
    '2d_3_px':'3 px 2D step', forward_50_mm_s:'50 mm/s forward speed', '2d_50_mm_s':'50 mm/s 2D speed',
};
const title = value => labels[value] || value.replaceAll('_', ' ');
const count = value => Number(value).toLocaleString();
const number = (value, digits=1) => value === null ? '—' : Number(value).toFixed(digits);
const svgNS = 'http://www.w3.org/2000/svg';

function options(id, values, allLabel, chosen) {
    const select = byId(id);
    if (allLabel) select.add(new Option(allLabel, ''));
    values.forEach(value => select.add(new Option(title(value), value)));
    if (chosen !== undefined) select.value = chosen;
}

function table(id, headings, rows) {
    const target = byId(id);
    const head = document.createElement('thead');
    const line = head.insertRow();
    for (const heading of headings) {
        const cell = document.createElement('th');
        cell.scope = 'col';
        cell.textContent = heading;
        line.append(cell);
    }
    const body = document.createElement('tbody');
    for (const values of rows) {
        const row = body.insertRow();
        for (const value of values) row.insertCell().textContent = value;
    }
    target.replaceChildren(head, body);
}

function updateTiming() {
    const subject = byId('timingSubject').value || 'all';
    const marker = byId('timingMarker').value;
    const scope = byId('timingScope').value;
    const family = marker === '400' ? 'movement' : 'jump';
    const rows = D.timing.filter(r => r.subject === subject && r.metric.startsWith(family));
    table('timingObserved', ['Observed interval', 'Trials', 'Median (ms)', '5th percentile (ms)', '95th percentile (ms)'],
        rows.map(r => [metricNames[r.metric], count(r.n), number(r.median_ms,2), number(r.p05_ms,2), number(r.p95_ms,2)]));
    const comparisons = D.comparison.filter(r => (r.subject || 'all') === subject && r.marker === marker && r.fit_scope === scope);
    comparisons.sort((a,b) => Number(b.exact_pct)-Number(a.exact_pct));
    const shared = scope === 'shared';
    const fixed = scope === 'fixed';
    byId('timingSharedNote').hidden = !shared;
    const fixedNote = byId('timingFixedNote');
    fixedNote.hidden = !fixed;
    fixedNote.textContent = marker === '400'
        ? 'The draft specifies 50 mm/s for longitudinal movement onset and offset using smoothed trajectories. These benchmarks use the logged cursor samples.'
        : 'These jump cutoffs are exploratory references drawn from these recordings. The draft describes the jump as timed to movement onset without specifying a separate numerical cutoff.';
    const cutoffRows = shared ? D.sharedCutoffs.filter(r => r.marker === marker) : [];
    const cutoffFormat = new Intl.NumberFormat(undefined, {maximumFractionDigits: 3});
    const cutoffHeading = shared ? ['Shared cutoff'] : fixed ? ['Fixed cutoff'] : [];
    const headings = ['Candidate', ...cutoffHeading, 'Trials', 'Exact', 'Within ±6 ms', 'Within one sample'];
    const comparisonRows = comparisons.map(r => {
        const rule = fixed ? D.fixedCutoffs[marker][r.candidate] : null;
        const measure = rule ? rule[0] : r.candidate;
        const cells = [candidateNames[measure] || title(measure)];
        if (fixed) cells.push(rule ? cutoffFormat.format(rule[1]) : '—');
        if (shared) {
            const values = cutoffRows.filter(c => c.candidate === r.candidate && c.cutoff !== '')
                .sort((a,b) => Number(a.test_fold) - Number(b.test_fold))
                .map(c => Number(c.cutoff));
            cells.push([...new Set(values)].map(v => cutoffFormat.format(v)).join(' / ') || '—');
        }
        return cells.concat(count(r.trials), number(r.exact_pct)+'%', number(r.within_6ms_pct)+'%', number(r.within_one_sample_pct)+'%');
    });
    table('timingComparison', headings, comparisonRows);
}

function mark(svg, tag, attrs, text) {
    const node = document.createElementNS(svgNS, tag);
    for (const [key,value] of Object.entries(attrs)) node.setAttribute(key,value);
    if (text !== undefined) node.textContent = text;
    svg.append(node);
    return node;
}
function line(svg,x1,y1,x2,y2,color,dashes) {
    const attrs = {x1,y1,x2,y2,stroke:color};
    if (dashes) attrs['stroke-dasharray'] = dashes;
    mark(svg,'line',attrs);
}

function extent(values, pad=.06) {
    const low = Math.min(...values), high = Math.max(...values);
    const margin = Math.max(1, (high-low)*pad);
    return [low-margin,high+margin];
}
function axes(id, xDomain, yDomain, xLabel, yLabel, {down=false, height=255, timeAxis=false}={}) {
    const svg = byId(id);
    svg.replaceChildren();
    const W=500, H=height, L=62, R=475, T=12, B=H-50;
    svg.setAttribute('viewBox','0 0 '+W+' '+H);
    const x = value => L+(value-xDomain[0])/(xDomain[1]-xDomain[0])*(R-L);
    const y = value => (down ? T : B)+(value-yDomain[0])/(yDomain[1]-yDomain[0])*(down ? B-T : T-B);
    const xSpan = xDomain[1]-xDomain[0];
    const ticks = [];
    if (timeAxis) {
        const step = Math.max(25, Math.ceil(xSpan/125)*25);
        for (let tick=Math.ceil(xDomain[0]/step)*step; tick<=xDomain[1]; tick+=step) ticks.push(tick);
    } else {
        for (let i=0;i<5;i++) ticks.push(xDomain[0]+i*xSpan/4);
    }
    for (const tick of ticks) {
        line(svg,x(tick),T,x(tick),B,'#e3eaf1');
        mark(svg,'text',{x:x(tick),y:B+16,'text-anchor':'middle',fill:'currentColor'},Math.round(tick));
    }
    for (let i=0;i<5;i++) {
        const ty=yDomain[0]+i*(yDomain[1]-yDomain[0])/4;
        line(svg,L,y(ty),R,y(ty),'#e3eaf1');
        mark(svg,'text',{x:L-7,y:y(ty)+4,'text-anchor':'end',fill:'currentColor'},Math.round(ty));
    }
    mark(svg,'text',{x:(L+R)/2,y:H-9,'text-anchor':'middle',fill:'currentColor'},xLabel);
    mark(svg,'text',{x:15,y:(T+B)/2,transform:'rotate(-90 15 '+(T+B)/2+')','text-anchor':'middle',fill:'currentColor'},yLabel);
    return {svg,x,y,T,B,L,R};
}
function path(plot, pairs) {
    mark(plot.svg,'polyline',{points:pairs.map(([x,y]) => plot.x(x).toFixed(2)+','+plot.y(y).toFixed(2)).join(' '),
        fill:'none',stroke:colors.cursor,'stroke-width':2});
}
function point(plot, coords, color, label, ring=false) {
    if (!coords) return;
    const node = mark(plot.svg,'circle',{cx:plot.x(coords[0]),cy:plot.y(coords[1]),r:ring ? 6 : 4,
        fill:ring ? 'white' : color,stroke:color,'stroke-width':2});
    mark(node,'title',{},label+' ('+coords.join(', ')+')');
}
function empty(id, message) {
    const svg = byId(id);
    svg.setAttribute('viewBox','0 0 500 255');
    svg.replaceChildren();
    mark(svg,'text',{x:250,y:125,'text-anchor':'middle',fill:'currentColor'},message);
}

function drawPath(example) {
    const coords = example.points.map(([,x,y]) => [x,y]);
    const bounds = [...coords, example.initial_target, example.final_target];
    const [targetX, targetY] = example.final_target;
    const radius = example.hit_radius_px;
    if (radius) bounds.push([targetX-radius,targetY-radius],[targetX+radius,targetY+radius]);
    const xs = extent(bounds.map(p => p[0]));
    const ys = extent(bounds.map(p => p[1]));
    // Keep a cursor pixel the same size on both axes.
    const plotHeight = 380;
    const aspect = (475-62)/(plotHeight-50-12);
    const xWidth = xs[1]-xs[0], yWidth = ys[1]-ys[0];
    const width = Math.max(xWidth,yWidth*aspect), height=width/aspect;
    const cx=(xs[0]+xs[1])/2, cy=(ys[0]+ys[1])/2;
    const plot = axes('reachPath',[cx-width/2,cx+width/2],[cy-height/2,cy+height/2],'Cursor x (px)','Cursor y (px)',{down:true,height:plotHeight});
    if (radius) {
        const circle = mark(plot.svg,'circle',{cx:plot.x(targetX),cy:plot.y(targetY),
            r:plot.x(targetX+radius)-plot.x(targetX),fill:'none',stroke:colors.hit,'stroke-dasharray':'3 3'});
        mark(circle,'title',{},'Provisional target radius ('+radius+' px)');
    }
    path(plot,coords);
    point(plot,example.movement_xy,colors.neutral,'Movement onset');
    point(plot,example.initial_target,colors.neutral,'Initial target center',true);
    if (example.jump_direction) point(plot,example.final_target,colors.jump,'Final target center',true);
    point(plot,example.jump_xy,colors.jump,'Cursor at jump');
    point(plot,example.steering_xy,colors.steer,'Cursor at detected steering onset');
    point(plot,example.outward_end_xy,colors.neutral,'Estimated outward end',true);
    point(plot,example.closest_xy,colors.cursor,'Closest observed approach',true);
    point(plot,example.endpoint_xy,colors.end,'Manuscript endpoint');
    point(plot,example.first_hit_xy,colors.hit,'First target entry');
}
function drawTime(example, speedPlot) {
    const id = speedPlot ? 'reachSpeed' : 'reachLateral';
    const origin = example.jump_ms_from_movement ?? 0;
    const referenceX = (example.jump_xy || example.movement_xy)[0];
    const sign = example.jump_direction || 1;
    const pairs = example.points.map(([time,x,,speed]) => [time-origin,speedPlot ? speed : sign*(x-referenceX)])
        .filter(p => p[1] !== null);
    if (!pairs.length) {
        empty(id,'No samples for this measure');
        return;
    }
    const marks = [
        [-origin,colors.neutral,'Movement onset'],
        [example.jump_direction ? 0 : null,colors.jump,'Target jump'],
        [example.endpoint_xy ? example.endpoint_ms_from_movement-origin : null,colors.end,'Verified endpoint'],
        [example.first_hit_ms_from_anchor ?? null,colors.hit,'First target entry'],
        [example.outward_steering_ms_from_jump,colors.steer,'Steering onset'],
        [example.outward_end_ms_from_movement === null ? null : example.outward_end_ms_from_movement-origin,colors.neutral,'Estimated outward end'],
        [example.jump_direction && pairs.at(-1)[0] >= 250 ? 250 : null,colors.neutral,'250 ms observation window'],
    ];
    const values = pairs.map(p => p[1]);
    if (speedPlot && example.jump_direction) values.push(150);
    const plot = axes(id,extent(pairs.map(p => p[0]),0),extent(values), 'Time from '+(example.jump_direction ? 'jump' : 'movement')+' (ms)',
        speedPlot ? 'Lateral speed (mm/s)' : 'Lateral displacement (px)', {timeAxis:true});
    if (speedPlot && example.jump_direction) line(plot.svg,plot.L,plot.y(150),plot.R,plot.y(150),colors.steer,'4 4');
    for (const [time,color,label] of marks) {
        if (time === null) continue;
        const bar = mark(plot.svg,'line',{x1:plot.x(time),x2:plot.x(time),y1:plot.T,y2:plot.B,stroke:color,'stroke-dasharray':'3 4'});
        mark(bar,'title',{},label);
    }
    path(plot,pairs);
}

function histogram(values, chosen) {
    if (!values.length) {
        empty('reachDistances','No verified endpoints in this selection');
        return;
    }
    const max = values.reduce((a,b) => Math.max(a,b),0);
    const binWidth = Math.max(10,Math.ceil(max/200)*10);
    const bins = new Array(Math.max(1,Math.ceil(max/binWidth))).fill(0);
    values.forEach(v => bins[Math.min(bins.length-1,Math.floor(v/binWidth))]++);
    const plot = axes('reachDistances',[0,bins.length*binWidth],[0,Math.max(...bins)],'Distance to final target center (px)','Trials');
    bins.forEach((n,i) => {
        const x = plot.x(i*binWidth), right=plot.x((i+1)*binWidth);
        const bar = mark(plot.svg,'rect',{x:x+1,y:plot.y(n),width:right-x-2,height:plot.B-plot.y(n),fill:'#6192b9'});
        mark(bar,'title',{},count(n)+' trials · '+i*binWidth+'–'+(i+1)*binWidth+' px');
    });
    if (chosen !== null) line(plot.svg,plot.x(chosen),plot.T,plot.x(chosen),plot.B,colors.end,'4 4');
}

function quantile(sorted,q) {
    if (!sorted.length) return null;
    const k=(sorted.length-1)*q, i=Math.floor(k);
    return sorted[i]+(sorted[Math.ceil(k)]-sorted[i])*(k-i);
}

const reachControls = ['reachSubject','reachSession','reachCondition','reachHit','reachSteering'];
const trialSelect = byId('reachTrial');
let shownExamples = [];
let distances = [];
function renderExample() {
    const example = shownExamples[Number(trialSelect.value)];
    const info = byId('reachTrialInfo');
    byId('reachHitLegend').hidden = !example?.hit_radius_px;
    histogram(distances,example ? example.filters[7] : null);
    if (!example) {
        info.textContent = 'No saved example matches this selection.';
        ['reachPath','reachLateral','reachSpeed'].forEach(id => empty(id,'No matching example'));
        return;
    }
    const [,session,condition,outcome,steering,accepted,,distance,closest] = example.filters;
    const side = example.jump_direction === 1 ? 'right jump' : example.jump_direction === -1 ? 'left jump' : 'no jump';
    const endpoint = distance === null ? 'Endpoint unavailable' : 'Endpoint '+number(distance)+' px from final target center';
    info.textContent = [
        example.run+' / trial '+example.trial, session, side,
        title(outcome), condition === 'D' ? 'Steering '+title(steering) : '',
        example.first_hit_ms_from_anchor != null
            ? 'First entry at '+number(example.first_hit_ms_from_anchor)+' ms' : '',
        endpoint, closest === null ? '' : 'Closest outward '+number(closest)+' px',
        example.full_log_min_distance_px != null ? 'Closest full log '+number(example.full_log_min_distance_px)+' px' : '',
        example.outward_end_reason ? 'Outward end: '+example.outward_end_reason.replaceAll('_',' ') : '', accepted ? 'EEG accepted' : 'Not in EEG-accepted selection',
    ].filter(Boolean).join(' · ');
    drawPath(example);
    drawTime(example,false);
    drawTime(example,true);
}

function updateReaches() {
    const selections = reachControls.map(id => byId(id).value);
    const acceptedOnly = byId('reachAccepted').checked;
    const matches = row => selections.every((value,i) => !value || row[i] === value)
        && (!acceptedOnly || row[5] === 1);
    const selected = D.reaches.filter(matches);
    distances = selected.map(row => row[7]).filter(v => v !== null);
    const linked = selected.filter(r => r[6] === 1).length;
    const early = selected.filter(r => r[4] === 'early').length;
    byId('reachSummary').textContent = count(selected.length)+' trials · '+count(linked)+' linked behavioural rows · '
        +count(distances.length)+' verified endpoints · '+count(early)+' early steering detections.';
    const summaries = [];
    for (const session of sessions) {
        for (const condition of ['D','ND']) {
            const group = selected.filter(r => r[1] === session && r[2] === condition);
            if (!group.length) continue;
            const d = group.map(r => r[7]).filter(v => v !== null).sort((a,b) => a-b);
            const closest = group.map(r => r[8]).filter(v => v !== null).sort((a,b) => a-b);
            summaries.push([session+' · '+condition,count(group.length),count(group.filter(r => r[5] === 1).length),
                count(d.length),condition === 'ND' ? '—' : count(group.filter(r => r[4] === 'early').length),
                number(quantile(d,.5)),d.length ? number(quantile(d,.1))+'–'+number(quantile(d,.9)) : '—',
                number(quantile(closest,.5))]);
        }
    }
    table('reachCounts',['Session and class','Trials','EEG accepted','Verified endpoints','Early steering',
        'Median endpoint (px)','10th–90th endpoint (px)','Median closest (px)'],summaries);
    const previous = shownExamples[Number(trialSelect.value)];
    shownExamples = D.examples.filter(example => matches(example.filters));
    trialSelect.replaceChildren();
    shownExamples.forEach((example,i) => trialSelect.add(new Option(
        example.filters[0]+' · '+example.filters[1]+' · '+example.run.split('_').at(-2)+' / '+example.trial+' · '+
        title(example.filters[3])+' · '+(example.filters[7] === null ? 'endpoint unavailable' : number(example.filters[7])+' px'),i
    )));
    const retained = shownExamples.indexOf(previous);
    if (retained >= 0) trialSelect.value = retained;
    trialSelect.disabled = !shownExamples.length;
    renderExample();
}

options('timingSubject',D.subjects,'All participants');
options('reachSubject',D.subjects,'All participants',D.subjects[0]);
options('reachSession',sessions,'All sessions','pre');
options('reachSteering',[...new Set(D.reaches.map(r => r[4]))].sort(),'All steering groups');
options('reachHit',['hit_detected','no_hit_detected','not_assessed'],'All outcomes');
byId('reachHitField').hidden = !D.targetHits.length;
byId('reachCondition').value = 'D';
['timingSubject','timingMarker','timingScope'].forEach(id => byId(id).addEventListener('change',updateTiming));
[...reachControls,'reachAccepted'].forEach(id => byId(id).addEventListener('change',updateReaches));
trialSelect.addEventListener('change',renderExample);
updateTiming();
updateReaches();

if (D.targetHits.length) {
    byId('target-hits').hidden = false;
    byId('targetHitsLink').hidden = false;
    options('hitSubject', [...new Set(D.targetHits.map(r => r[0]))].sort(), 'All participants');
    options('hitSession', sessions, 'All sessions');
    byId('hitRadiusField').hidden = !D.closeApproachAvailable;
    function updateHits() {
        const subject = byId('hitSubject').value;
        const session = byId('hitSession').value;
        const radius = byId('hitRadius').value;
        const hit = radius === '40';
        const index = hit ? 3 : radius === '75' ? 5 : 6;
        byId('observedHitScope').hidden = !hit;
        byId('closeApproachScope').hidden = hit;
        const selected = D.targetHits.filter(([who, visit]) => (!subject || who === subject) && (!session || visit === session));
        const summary = [['D', 'Displaced (D)'], ['ND', 'Non-displaced (ND)']].map(([condition, label]) => {
            const totals = selected.filter(r => r[2] === condition).reduce(([inside, outside], r) =>
                [inside + r[index], outside + r[3] + r[4] - r[index]], [0, 0]);
            return [label, ...totals.map(count)];
        });
        const headings = hit ? ['Hit detected', 'No hit detected'] : ['Within '+radius+' px', 'No approach within '+radius+' px'];
        table('hitCounts', ['Trial condition', ...headings], summary);
    }
    ['hitSubject', 'hitSession', 'hitRadius'].forEach(id => byId(id).addEventListener('change', updateHits));
    updateHits();
}

if (location.hostname === 'htmlpreview.github.io') {
    const base = 'https://github.com/neurocontrol-lab/mouse-displacement-eeg/blob/main/output/AUD_data_audit/report/index.html';
    for (const link of document.querySelectorAll('a[href]')) {
        const href = link.getAttribute('href');
        if (href.startsWith('#')) continue;
        const url = new URL(href,base);
        link.href = url.pathname.endsWith('/index.html') ? 'https://htmlpreview.github.io/?'+url.href : url.href;
    }
}
