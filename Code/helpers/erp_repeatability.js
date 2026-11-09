
{
    const rows = title => D.tables.find(table => table.title === title).rows;
    const participants = rows('Participant amplitudes (pooled sessions)');
    const sessions = rows('Participant/session amplitudes');
    const runs = rows('Recording amplitudes');
    const windows = rows('Non-pilot group tests');
    const subjects = D.erp.subjects;
    const windowSelect = byId('erpRepeatWindow');
    const personSelect = byId('erpRepeatSubject');
    const forest = byId('erpRepeatForest');
    const detail = byId('erpRepeatRuns');

    for (const [i, win] of windows.entries()) {
        const alignment = win.alignment === 'jump' ? 'Jump' : 'Movement';
        windowSelect.add(new Option(
            alignment + ' · ' + win.component_window + ' · ' + win.start_ms + '–' +
            win.end_ms_exclusive + ' ms · ' + win.electrodes, i
        ));
    }
    for (const subject of subjects) {
        const pilot = D.erp.cohorts[subject] === 'pilot' ? ' (pilot)' : '';
        personSelect.add(new Option(subject + pilot, subject));
    }

    function mark(parent, tag, attributes, text) {
        const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
        for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
        if (text !== undefined) node.textContent = text;
        parent.append(node);
        return node;
    }

    function axes(svg, labels, limit, spacing) {
        svg.replaceChildren();
        const width = 520, left = 102, right = width - 20;
        const top = 12, bottom = top + labels.length * spacing;
        const height = bottom + 42;
        svg.setAttribute('viewBox', '0 0 ' + width + ' ' + height);
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        const x = value => left + (Number(value) + limit) * (right - left) / (2 * limit);
        const y = row => top + (row + 0.5) * spacing;
        for (let i = 0; i < labels.length; i++) {
            mark(svg, 'line', {x1: left, x2: right, y1: y(i), y2: y(i), stroke: '#e7edf3'});
            mark(svg, 'text', {x: left - 9, y: y(i) + 4, 'text-anchor': 'end', fill: 'currentColor'}, labels[i]);
        }
        for (const tick of [-limit, -limit / 2, 0, limit / 2, limit]) {
            mark(svg, 'line', {x1: x(tick), x2: x(tick), y1: top, y2: bottom, stroke: tick ? '#e7edf3' : '#8291a2'});
            mark(svg, 'text', {x: x(tick), y: bottom + 15, 'text-anchor': 'middle', fill: 'currentColor'}, tick);
        }
        mark(svg, 'text', {x: (left + right) / 2, y: height - 7, 'text-anchor': 'middle', fill: 'currentColor'}, 'D − ND (µV)');
        return {x, y};
    }

    const labelValue = value => Number(value).toFixed(2) + ' µV';
    const extent = values => Math.max(1, Math.ceil(Math.max(...values.map(v => Math.abs(v)))));

    function renderRepeatability() {
        const window = windows[Number(windowSelect.value)];
        const subject = personSelect.value;
        const inWindow = row => row.alignment === window.alignment && row.component_window === window.component_window;
        const effects = participants.filter(inWindow);
        const chosen = effects.find(row => row.subject === subject);
        const labels = effects.map(row => row.subject + (row.cohort === 'pilot' ? ' *' : ''));
        const limit = extent(effects.flatMap(row => [row.bootstrap95_low_uV, row.D_minus_ND_uV, row.bootstrap95_high_uV]));
        const pooled = axes(forest, labels, limit, 20);
        effects.forEach((row, i) => {
            const color = row.subject === subject ? '#075da8' : '#53657a';
            const y = pooled.y(i);
            const range = mark(forest, 'line', {
                x1: pooled.x(row.bootstrap95_low_uV), x2: pooled.x(row.bootstrap95_high_uV),
                y1: y, y2: y, stroke: color, 'stroke-width': 2
            });
            const point = mark(forest, 'circle', {cx: pooled.x(row.D_minus_ND_uV), cy: y, r: 4, fill: color});
            const tooltip = row.subject + ' · ' + labelValue(row.D_minus_ND_uV) + ' · 95% interval '
                + labelValue(row.bootstrap95_low_uV) + ' to ' + labelValue(row.bootstrap95_high_uV);
            mark(point, 'title', {}, tooltip);
            mark(range, 'title', {}, tooltip);
        });

        const perSession = sessions.filter(row => row.subject === subject && inWindow(row));
        const perRun = runs.filter(row => row.subject === subject && inWindow(row));
        const ordered = D.erp.sessions.map(visit => perSession.find(row => row.session === visit)).filter(Boolean);
        const runLimit = extent(perRun.map(row => row.D_minus_ND_uV));
        const spread = axes(detail, ordered.map(row => row.session + ' (' + row.runs + ')'), runLimit, 65);
        ordered.forEach((session, i) => {
            const visitRuns = perRun.filter(row => row.session === session.session);
            const y = spread.y(i);
            visitRuns.forEach((row, j) => {
                const cy = y + (j - (visitRuns.length - 1) / 2) * 8;
                const point = mark(detail, 'circle', {cx: spread.x(row.D_minus_ND_uV), cy, r: 4, fill: '#8291a2'});
                mark(point, 'title', {}, row.run + ' · ' + labelValue(row.D_minus_ND_uV) + ' · ' + row.matched_pairs + ' pairs');
            });
            const x = spread.x(session.D_minus_ND_uV);
            const diamond = mark(detail, 'polygon', {points: [
                [x, y - 5], [x + 5, y], [x, y + 5], [x - 5, y]
            ].map(p => p.join(',')).join(' '), fill: '#075da8'});
            mark(diamond, 'title', {}, session.session + ' · ' + labelValue(session.D_minus_ND_uV));
        });
        byId('erpRepeatEstimate').textContent = personSelect.selectedOptions[0].textContent + ' · '
            + labelValue(chosen.D_minus_ND_uV) + ' pooled · 95% interval '
            + labelValue(chosen.bootstrap95_low_uV) + ' to ' + labelValue(chosen.bootstrap95_high_uV)
            + ' · ' + chosen.runs + ' runs · ' + chosen.matched_pairs + ' matched pairs.';
        const list = byId('erpRepeatSessionList');
        list.replaceChildren();
        for (const row of ordered) {
            const item = document.createElement('li');
            item.textContent = row.session + ' · ' + labelValue(row.D_minus_ND_uV) + ' · '
                + row.runs + (row.runs === '1' ? ' run · limited repeatability evidence' : ' runs')
                + ' · ' + row.matched_pairs + ' pairs';
            list.append(item);
        }
    }

    windowSelect.addEventListener('change', renderRepeatability);
    personSelect.addEventListener('change', renderRepeatability);
    renderRepeatability();
}
