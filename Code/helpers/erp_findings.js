{
    function setCell(cell, content) {
        for (const [i, line] of [].concat(content).entries()) {
            if (i) cell.append(document.createElement('br'));
            cell.append(String(line));
        }
    }

    function fillTable(id, headings, values, emphasized = []) {
        const table = byId(id);
        const head = document.createElement('thead');
        const header = head.insertRow();
        for (const name of headings) {
            const cell = document.createElement('th');
            cell.scope = 'col';
            setCell(cell, name);
            header.append(cell);
        }
        const body = document.createElement('tbody');
        values.forEach((fields, i) => {
            const row = body.insertRow();
            if (emphasized[i]) row.className = 'erp-supported';
            for (const field of fields) setCell(row.insertCell(), field);
        });
        table.replaceChildren(head, body);
    }

    const getRows = title => D.tables.find(table => table.title === title)?.rows ?? [];
    const signed = value => (value > 0 ? '+' : '') + Number(value).toFixed(2).replace('-', '−');
    const interval = (start, end) => start + '–' + end + ' ms';
    const alignLabel = alignment => alignment === 'jump' ? 'Jump' : 'Movement';
    const svgNS = 'http://www.w3.org/2000/svg';

    function mark(svg, tag, attrs, value) {
        const node = document.createElementNS(svgNS, tag);
        for (const [key, val] of Object.entries(attrs)) node.setAttribute(key, val);
        if (value !== undefined) node.textContent = value;
        svg.append(node);
        return node;
    }

    function forest(rows) {
        const svg = byId('erpTestForest');
        const left = 246, right = 755, top = 16, bottom = top + rows.length * 29;
        svg.setAttribute('viewBox', '0 0 770 ' + (bottom + 45));
        svg.replaceChildren();
        const lo = Math.min(0, ...rows.map(r => Number(r.ci95_low_uV)));
        const hi = Math.max(0, ...rows.map(r => Number(r.ci95_high_uV)));
        const min = Math.floor(lo), max = Math.ceil(hi);
        const x = value => left + (value - min) / (max - min) * (right - left);
        for (let tick = min; tick <= max; tick++) {
            mark(svg, 'line', {x1:x(tick), x2:x(tick), y1:top, y2:bottom,
                stroke:tick === 0 ? '#53657a' : '#e1e8ef'});
            mark(svg, 'text', {x:x(tick), y:bottom+16, 'text-anchor':'middle', fill:'currentColor'}, tick);
        }
        rows.forEach((row, i) => {
            const y = top + (i+.5)*29;
            const color = Number(row.p_Holm) < .05 ? '#075da8' : '#74879c';
            mark(svg, 'text', {x:3, y:y+4, fill:'currentColor'},
                row.component_window + ' · ' + alignLabel(row.alignment) + ' · ' + interval(row.start_ms,row.end_ms_exclusive));
            mark(svg, 'line', {x1:x(row.ci95_low_uV), x2:x(row.ci95_high_uV), y1:y, y2:y, stroke:color, 'stroke-width':2.5});
            const point = mark(svg, 'circle', {cx:x(row.mean_D_minus_ND_uV), cy:y, r:4.7, fill:color});
            mark(point,'title',{},row.electrodes+' · '+signed(row.mean_D_minus_ND_uV)+' µV · Holm p = '+Number(row.p_Holm).toFixed(4));
        });
        mark(svg, 'text', {x:(left+right)/2, y:bottom+36, 'text-anchor':'middle', fill:'currentColor'}, 'Mean D − ND (µV)');
    }

    const choices = [
        {id:'d_nd_hit', label:'D hits vs matched ND hits · ERP_04', rows:getRows('ERP_04 matched-hit window tests (exploratory)'), exploratory:true},
        {id:'all_d_nd', label:'All D vs matched ND · ERP_01', rows:getRows('Non-pilot group tests'), exploratory:false},
    ].filter(choice => choice.rows.length);
    const selector = byId('erpTestContrast');
    choices.forEach(choice => selector.add(new Option(choice.label,choice.id)));
    const selectedTests = () => choices.find(choice => choice.id === selector.value);

    function updateTests() {
        const {rows,exploratory} = selectedTests();
        const supported = rows.filter(r => Number(r.p_Holm) < .05);
        const headline = supported.map(r => r.electrodes.replaceAll('/', ' / ') + ', ' +
            interval(r.start_ms,r.end_ms_exclusive) + ' ' + alignLabel(r.alignment).toLowerCase() +
            ' (' + signed(r.mean_D_minus_ND_uV) + ' µV, Holm p = ' + Number(r.p_Holm).toFixed(4) + ')');
        byId('erpTestSummary').textContent = (exploratory ? 'In the matched-hit comparison, ' : '') +
            (headline.length ? headline.join(' and ') + ' met the adjusted .05 threshold.' : 'The selected tests are shown below.');
        byId('erpTestMethod').textContent = (exploratory ? 'Exploratory follow-up. ' : 'ERP_01 fixed-window tests. ') +
            rows[0].participants + ' non-pilot participants' + (rows[0].matched_pairs ? ' and ' +
                Number(rows[0].matched_pairs).toLocaleString() + ' pairs' : '') +
            '. Two-sided tests use one paired estimate per participant, pooled across sessions. Holm adjustment covers the ' +
            rows.length + ' windows in this contrast.';
        forest(rows);
        fillTable('erpTestValues', ['Alignment','Window','Electrodes','Interval','Mean D − ND (µV)','95% CI (µV)','Holm p'],
            rows.map(r => [alignLabel(r.alignment),r.component_window,r.electrodes,
                interval(r.start_ms,r.end_ms_exclusive),signed(r.mean_D_minus_ND_uV),
                signed(r.ci95_low_uV)+' to '+signed(r.ci95_high_uV),Number(r.p_Holm).toFixed(4)]),
            rows.map(r => Number(r.p_Holm) < .05));
    }
    if (choices.length) {
        byId('erpTestWaveform').onclick = () => {
            const contrast = byId('erpContrast');
            contrast.value = selectedTests().exploratory ? 'hits' : 'all';
            contrast.dispatchEvent(new Event('change'));
        };
        selector.onchange = updateTests;
        updateTests();
    }

    const hitClusterPlot = D.figures.find(f => f.name === 'matched_hit_clusters');
    const clusters = getRows('ERP_04 matched-hit clusters').filter(r => Number(r.p_cluster) < .05);
    const clusterSessions = getRows('ERP_04 matched-hit cluster session estimates');
    const [n100] = getRows('ERP_04 posterior N100 check');
    if (hitClusterPlot && n100) {
        byId('erpHitTimingResults').hidden = false;
        byId('erpHitClusterPlot').src = hitClusterPlot.src;
        byId('erpHitTimingScope').textContent = 'A hit required observed entry into a circle with a 40 px radius around the final target center. '
            + 'Time zero is the recorded target jump on D trials. On each matched ND trial, the pseudo-jump is placed at the paired D trial’s jump delay after movement onset. '
            + n100.participants + ' non-pilot participants and ' + Number(n100.matched_pairs).toLocaleString()
            + ' pairs. The two-sided permutation test jointly corrects across 0–500 ms, both electrode groups and both polarities.';
        fillTable('erpHitClusterValues', ['Electrodes','Polarity','Observed interval','Mean D − ND (µV)','Corrected cluster p'],
            clusters.map(r => [r.electrodes,r.polarity,interval(r.start_ms,r.end_ms_exclusive),
                signed(r.mean_difference_uv),Number(r.p_cluster).toFixed(4)]));
        fillTable('erpHitClusterSessions', ['Electrodes','Pooled interval','Session','Participants','Pairs','Mean D − ND (µV)'],
            clusterSessions.map(r => [r.electrodes,interval(r.start_ms,r.end_ms_exclusive),r.session,
                r.participants,Number(r.matched_pairs).toLocaleString(),signed(r.mean_difference_uv)]));
        byId('erpHitN100').textContent = n100.electrodes + ', ' + interval(n100.start_ms,n100.end_ms_exclusive)
            + ' after the jump. Mean D − ND ' + signed(n100.mean_difference_uv) + ' µV (marginal 95% CI '
            + signed(n100.ci95_low_uV) + ' to ' + signed(n100.ci95_high_uV) + ' µV, p = ' + Number(n100.p).toFixed(4) + ').';
    }

    const distancePlot = D.figures.find(f => f.name === 'distance_associations');
    const slopes = getRows('ERP_02 distance slope summary');
    const measures = [
        ['full_log_min_distance_px','Full eligible log (primary)','Minimum over all eligible samples, including later approaches'],
        ['closest_distance_px','Outward reach','Minimum up to the estimated outward endpoint'],
        ['endpoint_distance_px','Manuscript endpoint','Distance at the verified original endpoint'],
    ];
    if (distancePlot && slopes.length) {
        byId('erp-distance').hidden = false;
        const selection = byId('erpDistanceSelection');
        const plots = D.erpDistancePlots ?? {};
        for (const [id, name] of [['hit_detected','D · observed hit'], ['no_hit_detected','D · no hit detected']]) {
            if (plots[id] && slopes.some(row => row.selection === id)) selection.add(new Option(name, id, false, id === 'hit_detected'));
        }
        function updateDistance() {
            const selected = slopes.filter(row => (row.selection ?? 'all') === selection.value);
            byId('erpDistancePlot').src = plots[selection.value] ?? distancePlot.src;
            const trials = Number(selected[0].eligible_trials ?? 9628).toLocaleString();
            const participants = Math.max(...selected.map(row => Number(row.participants)));
            const rangeNote = selection.value === 'hit_detected'
                ? ' The full-log distance in hits is bounded by 40 px. The 100 px unit scales the fitted slope.' : '';
            byId('erpDistanceScope').textContent = trials + ' eligible D trials · Up to ' + participants
                + ' non-pilot participants with estimable slopes.' + rangeNote;
            const interpretation = byId('erpDistanceInterpretation');
            const hitSlope = selected.find(row => row.selection === 'hit_detected'
                && row.distance === 'full_log_min_distance_px' && row.electrodes === 'Cz/FCz'
                && Number(row.start_ms) === 280 && Number(row.end_ms_exclusive) === 360);
            interpretation.hidden = !hitSlope;
            if (hitSlope) {
                const slope = Number(hitSlope.median_slope_uv_per_100px);
                const change = Math.abs(slope / 10).toFixed(2);
                const voltage = change === '0.00' ? 'approximately the same mean voltage'
                    : change + ' µV ' + (slope > 0 ? 'lower' : 'higher') + ' mean voltage';
                interpretation.textContent = 'Among observed hits, getting 10 px closer to the target center at closest approach '
                    + 'was associated with ' + voltage + ' at Cz/FCz from 280–360 ms after the jump. '
                    + 'This is the median within-participant slope for the full eligible log (' + signed(slope) + ' µV per 100 px).';
            }
            const rows = measures.flatMap(([id,name,definition]) => {
                const values = selected.filter(r => r.distance === id);
                if (!values.length) return [];
                const peak = values.reduce((a,b) => Math.abs(b.median_slope_uv_per_100px) >
                    Math.abs(a.median_slope_uv_per_100px) ? b : a);
                const central = values.find(r => r.electrodes === 'Cz/FCz'
                    && Number(r.start_ms) === 200 && Number(r.end_ms_exclusive) === 280);
                const strongest = [peak.component_window, peak.electrodes+' · '+interval(peak.start_ms,peak.end_ms_exclusive)];
                return [[name,definition,strongest,signed(peak.median_slope_uv_per_100px),
                    central ? signed(central.median_slope_uv_per_100px) : '—']];
            });
            fillTable('erpDistanceValues', ['Panel','Distance definition','Strongest ERP window',
                ['Median slope', '(µV/100 px)'],
                ['Interaction negativity', 'Cz/FCz · 200–280 ms', '(µV/100 px)']], rows);
        }
        selection.addEventListener('change', updateDistance);
        updateDistance();
    }
}

// Reveal the collapsible section linked by a report or experiment README.
function openERPSection() {
    const section = document.getElementById(window.location.hash.slice(1));
    if (section?.matches('#erp-window-tests, #erp-methods') && !section.open) {
        section.open = true;
        section.scrollIntoView();
    }
}
window.addEventListener('hashchange', openERPSection);
openERPSection();
