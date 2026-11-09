function setupERPFigureGallery(waveformView, panel) {
    const subject = byId('subject');
    const session = byId('session');
    const figure = byId('figure');
    const caption = byId('plotcaption');
    const holder = byId('erpFilteredFigure');
    const pairedNames = ['ND', 'D', 'D − ND'];
    const steeringNames = ['No early steering', 'Early steering', 'Early minus no early steering'];
    const palette = ['#1864a4', '#b05b16', '#27232b'];
    const steeringPalette = ['#53657a', '#137f6a', '#27232b'];
    const mainFigures = new Set([
        'matched_waveforms', 'movement_differences_by_session',
        'jump_differences_by_session', 'short_vs_long_delay',
    ]);
    const steeringFigures = new Set([
        'jump_early_steering', 'jump_control_subsets', 'jump_and_steering_alignment',
    ]);
    const trajectoryFigure = 'jump_corrective_vs_erroneous';
    const canFilter = f => mainFigures.has(f.name) || (D.erpSteering && steeringFigures.has(f.name))
        || (D.erpTrajectories && f.name === trajectoryFigure);

    subject.replaceChildren(new Option('All non-pilots', ''));
    option(subject, D.erp.subjects, false);
    session.replaceChildren(new Option('All sessions', ''));
    option(session, D.erp.sessions, false);
    byId('figureSubjectField').hidden = false;
    byId('figureSessionField').hidden = false;
    byId('figureScope').textContent =
        'Choose a participant or session to redraw the available waveform figures from saved means. ' +
        'With both filters set to All, the original summary figures are shown, including the pooled distance slopes.';

    function contrast(view, label) {
        return {view, label, curve: 2};
    }

    function regions(view) {
        const cz = view.traces[view.channels.indexOf('Cz')][2];
        const fcz = view.traces[view.channels.indexOf('FCz')][2];
        const cp1 = view.traces[view.channels.indexOf('CP1')][2];
        return {...view, channels: ['Cz / FCz', 'CP1'],
            traces: [[cz.map((value, i) => (value + fcz[i]) / 2)], [cp1]]};
    }

    async function figurePlots(name, who, visit) {
        const erp = (key, subset = 0, selectedVisit = visit) => waveformView(D.erp, key, who, selectedVisit, subset);
        const steering = (key, subset = 0) => waveformView(D.erpSteering, key, who, visit, subset);
        const alignments = [['Movement onset', 'movement'], ['Target jump / pseudo-jump', 'jump']];
        if (name === 'matched_waveforms') {
            return Promise.all(alignments.map(async ([title, key]) => {
                const view = await erp(key);
                return {title, series: pairedNames.map((label, curve) => ({view, label, curve}))};
            }));
        }
        if (name === 'short_vs_long_delay') {
            return Promise.all(alignments.map(async ([title, key]) => {
                const [short, long] = await Promise.all([erp(key, 1), erp(key, 2)]);
                return {title, series: [
                    {view: regions(short), label: 'Shorter delay · D − ND', curve: 0},
                    {view: regions(long), label: 'Longer delay · D − ND', curve: 0},
                ]};
            }));
        }
        if (name === 'movement_differences_by_session' || name === 'jump_differences_by_session') {
            const [title, key] = alignments[name === 'movement_differences_by_session' ? 0 : 1];
            const sessions = visit === 'all' ? D.erp.sessions : [visit];
            const series = await Promise.all(sessions.map(async s => contrast(await erp(key, 0, s), s + ' · D − ND')));
            return [{title, series}];
        }
        if (name === trajectoryFigure) {
            const view = await waveformView(D.erpTrajectories, 'jump', who, visit);
            const labels = ['Erroneous', 'Corrective', 'Corrective minus erroneous'];
            return [{title: 'Target jump', palette: steeringPalette,
                series: labels.map((label, curve) => ({view, label, curve}))}];
        }
        if (name === 'jump_early_steering') {
            const view = await steering('pairs');
            return [{title: 'Target jump', palette: steeringPalette, lineAt: 250,
                series: steeringNames.map((label, curve) => ({view, label, curve}))}];
        }
        if (name === 'jump_control_subsets') {
            const [later, none] = await Promise.all([steering('pairs', 1), steering('pairs', 2)]);
            return [{title: 'Target jump', series: [
                contrast(later, 'Early minus later steering'), contrast(none, 'Early minus no detection'),
            ]}];
        }
        const [jump, correction] = await Promise.all([steering('detected_jump'), steering('detected_steering')]);
        const delays = D.erpSteering.delay_ranges[who + '|' + visit];
        return [
            {title: 'Target jump', unit: 'trials', eventRange: delays,
                series: [{view: jump, label: 'Detected steering', curve: 0}]},
            {title: 'Steering onset', unit: 'trials', eventRange: delays?.map(ms => -ms).reverse(),
                series: [{view: correction, label: 'Detected steering', curve: 0}]},
        ];
    }

    function drawPlots(plots) {
        let extent = 1;
        for (const plot of plots) {
            for (const {view, curve} of plot.series.filter(s => s.view.pairs)) {
                for (const traces of view.traces) {
                    extent = Math.max(extent, ...traces[curve].map(Math.abs));
                }
            }
        }
        extent = Math.ceil(1.06 * extent);
        for (const plot of plots) {
            const heading = document.createElement('h3');
            heading.textContent = plot.title;
            const legend = document.createElement('p');
            legend.className = 'erp-legend';
            const series = plot.series.map((s, i) => ({...s, color: (plot.palette ?? palette)[i]}));
            const present = series.filter(s => s.view.pairs);
            for (const {view, label, color} of series) {
                const key = document.createElement('span');
                key.style.color = color;
                const n = view.pairs.toLocaleString();
                key.textContent = label + ' (' + n + ' ' + (plot.unit ?? 'pairs') + ')';
                legend.append(key);
            }
            holder.append(heading, legend);
            if (!present.length) {
                const message = document.createElement('p');
                message.textContent = 'No usable data for this selection.';
                holder.append(message);
                continue;
            }
            const grid = document.createElement('div');
            grid.className = 'grid';
            const {channels, desc} = present[0].view;
            for (const [i, channel] of channels.entries()) {
                const curves = present.map(s => s.view.traces[i][s.curve]);
                grid.append(panel(channel, desc, curves, extent, null, curves.map((_, k) => k), {
                    names: present.map(s => s.label),
                    palette: present.map(s => s.color),
                    eventLabel: plot.title,
                    lineAt: plot.lineAt,
                    eventRange: plot.eventRange,
                }));
            }
            holder.append(grid);
        }
    }

    let revision = 0;
    async function showSelection() {
        const current = ++revision;
        holder.replaceChildren();
        const filtered = Boolean(subject.value || session.value);
        holder.hidden = !filtered;
        if (!filtered) {
            showFigure();
            return;
        }
        byId('plot').hidden = true;
        const selected = D.figures.find(f => f.name === figure.value);
        byId('figureDescription').hidden = false;
        byId('figureDescription').textContent =
            'Waveforms for the current selection. Cohort means give each contributing non-pilot participant equal weight.'
            + (selected.name === trajectoryFigure ? ' ' + selected.description : '')
            + (selected.name === 'jump_and_steering_alignment'
                ? ' The amber band and dashed line mark the other event’s 5th–95th percentile range and median.' : '');
        caption.textContent = selected.title + ' · ' + (subject.value || 'Non-pilot cohort')
            + ' · ' + (session.value || 'Pooled sessions');
        holder.textContent = 'Loading selected waveforms…';
        try {
            const plots = await figurePlots(selected.name, subject.value || 'validation', session.value || 'all');
            if (current !== revision) return;
            holder.replaceChildren();
            drawPlots(plots);
        } catch (error) {
            if (current !== revision) return;
            holder.textContent = 'Could not load the selected waveforms.';
            console.error(error);
        }
    }

    function updateSelection() {
        const previous = figure.value;
        const available = subject.value || session.value ? D.figures.filter(canFilter) : D.figures;
        figure.replaceChildren(...available.map(f => new Option(f.title, f.name)));
        if (available.some(f => f.name === previous)) figure.value = previous;
        showSelection();
    }
    figure.onchange = showSelection;
    subject.onchange = session.onchange = updateSelection;
    updateSelection();
}
