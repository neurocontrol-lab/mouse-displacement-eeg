{
    function fillTable(id, headings, values, emphasized = []) {
        const table = byId(id);
        const head = document.createElement('thead');
        const header = head.insertRow();
        for (const name of headings) {
            const cell = document.createElement('th');
            cell.scope = 'col';
            cell.textContent = name;
            header.append(cell);
        }
        const body = document.createElement('tbody');
        values.forEach((fields, i) => {
            const row = body.insertRow();
            if (emphasized[i]) row.className = 'erp-supported';
            for (const field of fields) row.insertCell().textContent = field;
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
            const figure = byId('figure');
            figure.value = selectedTests().exploratory ? 'outcome_d_nd_hit' : 'matched_waveforms';
            figure.dispatchEvent(new Event('change'));
        };
        selector.onchange = updateTests;
        updateTests();
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
        byId('erpDistancePlot').src = distancePlot.src;
        const rows = measures.flatMap(([id,name,definition]) => {
            const values = slopes.filter(r => r.distance === id);
            if (!values.length) return [];
            const peak = values.reduce((a,b) => Math.abs(b.median_slope_uv_per_100px) >
                Math.abs(a.median_slope_uv_per_100px) ? b : a);
            const central = values.find(r => r.electrodes === 'Cz/FCz'
                && Number(r.start_ms) === 200 && Number(r.end_ms_exclusive) === 280);
            const strongest = peak.component_window+' · '+peak.electrodes+' · '+interval(peak.start_ms,peak.end_ms_exclusive);
            return [[name,definition,strongest,signed(peak.median_slope_uv_per_100px),
                central ? signed(central.median_slope_uv_per_100px) : '—']];
        });
        fillTable('erpDistanceValues', ['Panel','Distance definition','Strongest ERP window',
            'Median slope (µV/100 px)','Interaction negativity window · Cz/FCz, 200–280 ms (µV/100 px)'], rows);
    }
}
