{
    const report = D.erp;
    const scope = byId('erpSubject');
    const session = byId('erpSession');
    const alignment = byId('erpAlignment');
    const delay = byId('erpDelay');
    const highlight = byId('erpWindow');
    const grid = byId('erpWaves');
    const countsNote = byId('erpCounts');
    const colors = ['#1f5a96', '#aa4834', '#27232b'];
    const toggles = [...document.querySelectorAll('.erp-legend input')];
    const cohortOptions = {'validation': 'Non-pilot cohort', 'pilot': 'Two pilot participants'};
    for (const [value, label] of Object.entries(cohortOptions)) {
        scope.add(new Option(label, value));
    }
    for (const [value, label] of Object.entries(cohortOptions)) {
        const group = document.createElement('optgroup');
        group.label = label;
        for (const subject of report.subjects.filter(s => report.cohorts[s] === value)) {
            group.append(new Option(subject, subject));
        }
        scope.append(group);
    }
    report.sessions.forEach(s => session.add(new Option(s, s)));

    const tests = D.tables.find(table => table.title === 'Non-pilot group tests').rows;
    function windowOptions() {
        highlight.replaceChildren(new Option('None', ''));
        tests.forEach((test, i) => {
            if (test.alignment === alignment.value) {
                highlight.add(new Option(
                    test.component_window + ' (' + test.start_ms + '–' + test.end_ms_exclusive + ' ms)', i
                ));
            }
        });
    }

    const decoded = new Map();
    function loadSamples(data, descriptor) {
        if (!decoded.has(descriptor)) {
            const packed = Uint8Array.from(atob(descriptor.gzip), c => c.charCodeAt(0));
            const stream = new Blob([packed]).stream().pipeThrough(new DecompressionStream('gzip'));
            decoded.set(descriptor, new Response(stream).arrayBuffer().then(buffer => {
                const expected = data.subjects.length * data.sessions.length * (descriptor.subsets ?? 3)
                    * (descriptor.classes ?? 2) * data.channels.length * descriptor.samples * 2;
                if (buffer.byteLength !== expected) throw new Error('Unexpected waveform size.');
                const values = new DataView(buffer);
                const seriesBytes = 2 * descriptor.samples;
                for (let start = 0; start < buffer.byteLength; start += seriesBytes) {
                    let voltage = 0;
                    for (let byte = start; byte < start + seriesBytes; byte += 2) {
                        voltage += values.getInt16(byte, true);
                        values.setInt16(byte, voltage, true);
                    }
                }
                return values;
            }));
        }
        return decoded.get(descriptor);
    }

    function combine(data, descriptor, samples, subjectScope, sessionScope, subset) {
        // Pool trials within a participant, then average the contributing participants.
        const size = descriptor.samples * data.channels.length * (descriptor.classes ?? 2);
        const counts = descriptor.counts ?? data.counts;
        const total = new Float64Array(size);
        let participants = 0, pairs = 0;
        for (const [i, subject] of data.subjects.entries()) {
            if (subject !== subjectScope && data.cohorts[subject] !== subjectScope) continue;
            const sum = new Float64Array(size);
            let subjectPairs = 0;
            for (const [j, visit] of data.sessions.entries()) {
                if (sessionScope !== 'all' && visit !== sessionScope) continue;
                const n = counts[i][j][subset];
                if (!n) continue;
                const offset = ((i * data.sessions.length + j) * (descriptor.subsets ?? 3) + subset) * size;
                for (let k = 0; k < size; k++) sum[k] += n * samples.getInt16(2 * (offset + k), true);
                subjectPairs += n;
            }
            if (!subjectPairs) continue;
            for (let k = 0; k < size; k++) total[k] += sum[k] / subjectPairs;
            pairs += subjectPairs;
            participants++;
        }
        return {pairs, participants, means: participants ? total.map(x => x / (participants * 100)) : total};
    }

    async function waveformView(data, key, subject, visit, subset = 0) {
        const desc = data.waveforms[key];
        const values = await loadSamples(data, desc);
        const {pairs, participants, means} = combine(data, desc, values, subject, visit, subset);
        const n = desc.samples;
        const channels = data.channels;
        const traces = channels.map((_, i) => {
            const first = [...means.subarray(i * n, (i + 1) * n)];
            if (desc.classes === 1) return [first];
            const offset = (channels.length + i) * n;
            const second = [...means.subarray(offset, offset + n)];
            return [first, second, second.map((v, j) => v - first[j])];
        });
        return {desc, channels, traces, pairs, participants};
    }

    function panel(channel, desc, curves, extent, window, visible, {
        names = ['ND', 'D', 'D − ND'], palette = colors,
        eventLabel = alignment.selectedOptions[0].textContent, lineAt, eventRange,
    } = {}) {
        const div = document.createElement('div');
        div.className = 'chart';
        const title = document.createElement('b');
        title.textContent = channel + ' (µV)';
        const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
        svg.setAttribute('class', 'erp-plot');
        svg.setAttribute('viewBox', '0 0 510 190');
        svg.setAttribute('role', 'img');
        svg.setAttribute('aria-label', channel + ' waveforms aligned to ' + eventLabel);
        const readout = document.createElement('p');
        readout.className = 'erp-cursor';
        readout.textContent = 'Point to a time to read amplitudes.';
        const left = 48, right = 495, top = 12, bottom = 150;
        const end = desc.first_ms + desc.step_ms * desc.samples;
        const x = time => left + (time - desc.first_ms) * (right - left) / (end - desc.first_ms);
        const y = voltage => bottom - (voltage + extent) * (bottom - top) / (2 * extent);
        const line = (x1, y1, x2, y2, color) =>
            '<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 + '" stroke="' + color + '"/>';
        const label = (x, y, value, anchor) =>
            '<text x="' + x + '" y="' + y + '" text-anchor="' + anchor + '" fill="currentColor">' + value + '</text>';
        let marks = '';
        if (eventRange) {
            const [lo, , hi] = eventRange;
            marks += '<rect x="' + x(lo) + '" y="' + top + '" width="' + (x(hi) - x(lo))
                + '" height="' + (bottom - top) + '" fill="#ffedcb"/>';
        }
        if (window && channel.split(' / ').every(ch => window.electrodes.split('/').includes(ch))) {
            const start = Math.max(window.start_ms, desc.first_ms);
            const stop = Math.min(window.end_ms_exclusive, end);
            if (stop > start) {
                marks += '<rect class="erp-window-shade" x="' + x(start) + '" y="' + top + '" width="'
                    + (x(stop) - x(start)) + '" height="' + (bottom - top) + '" fill="#d8eaf7"/>';
            }
        }
        for (let t = Math.ceil(desc.first_ms / 200) * 200; t <= end; t += 200) {
            marks += line(x(t), top, x(t), bottom, t === 0 ? '#596778' : '#d8e1eb');
            marks += label(x(t), bottom + 16, t, 'middle');
        }
        if (lineAt !== undefined) {
            marks += line(x(lineAt), top, x(lineAt), bottom, '#b5a58a');
        }
        if (eventRange) {
            const median = x(eventRange[1]);
            marks += '<line x1="' + median + '" x2="' + median + '" y1="' + top + '" y2="' + bottom
                + '" stroke="#a85416" stroke-dasharray="4 4"/>';
        }
        for (const voltage of [-extent, 0, extent]) {
            marks += line(left, y(voltage), right, y(voltage), voltage === 0 ? '#9babb9' : '#d8e1eb');
            marks += label(left - 6, y(voltage) + 4, voltage, 'end');
        }
        marks += label((left + right) / 2, 185, 'Time from event (ms)', 'middle');
        for (const i of visible) {
            const points = curves[i].map((v, j) =>
                x(desc.first_ms + j * desc.step_ms).toFixed(1) + ',' + y(v).toFixed(1));
            marks += '<polyline points="' + points.join(' ') + '" fill="none" stroke="' + palette[i]
                + '" stroke-width="' + (i === 2 ? '1.9' : '1.45') + '"/>';
        }
        svg.innerHTML = marks;
        svg.addEventListener('pointermove', event => {
            const bounds = svg.getBoundingClientRect();
            const px = (event.clientX - bounds.left) * 510 / bounds.width;
            const i = Math.round((px - left) * desc.samples / (right - left));
            if (i < 0 || i >= desc.samples) return;
            const values = visible.map(k => names[k] + ' ' + curves[k][i].toFixed(2) + ' µV');
            readout.textContent = (desc.first_ms + i * desc.step_ms) + ' ms · ' + values.join(' · ');
        });
        svg.addEventListener('pointerleave', () => {
            readout.textContent = 'Point to a time to read amplitudes.';
        });
        div.append(title, svg, readout);
        return div;
    }

    let revision = 0;
    async function render() {
        const current = ++revision;
        const key = alignment.value;
        const subset = Number(delay.value);
        const visible = toggles.filter(t => t.checked).map(t => Number(t.value));
        grid.replaceChildren();
        if (!visible.length) {
            countsNote.textContent = 'Select a waveform to display.';
            return;
        }
        countsNote.textContent = 'Loading waveforms…';
        try {
            const {desc, channels, traces, pairs, participants} = await waveformView(
                report, key, scope.value, session.value, subset
            );
            if (current !== revision) return;
            if (!pairs) {
                countsNote.textContent = 'No matched pairs for this selection.';
                return;
            }
            const scopeLabel = scope.selectedOptions[0].textContent;
            const visitLabel = session.selectedOptions[0].textContent;
            countsNote.textContent = scopeLabel + ' · ' + visitLabel + ' · ' + participants
                + (participants === 1 ? ' participant · ' : ' participants · ') + pairs.toLocaleString()
                + ' pairs (each class n=' + pairs.toLocaleString() + ').';
            // Keep the scale stable when toggling curves on the same selection.
            const extent = Math.max(1, Math.ceil(Math.max(...traces.flat(2).map(Math.abs)) * 1.06));
            const window = highlight.value === '' ? null : tests[Number(highlight.value)];
            grid.replaceChildren(...channels.map((ch, i) => panel(ch, desc, traces[i], extent, window, visible)));
        } catch (error) {
            if (current === revision) {
                countsNote.textContent = 'Could not read the embedded waveforms. The saved figures and tables are available below.';
                console.error(error);
            }
        }
    }

    for (const control of [scope, session, delay, highlight, ...toggles]) control.addEventListener('change', render);
    alignment.addEventListener('change', () => { windowOptions(); render(); });
    windowOptions();
    render();
    setupERPFigureGallery(waveformView, panel);
}
