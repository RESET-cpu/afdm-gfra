"""Plot saved denoising results, including the audited historical nine-curve study."""
from pathlib import Path
import hashlib
import math
from common import execute_public as execute
from data import PlotData, digest, load, read
import style


HISTORICAL_METHODS = ['proposed', 'proposed_small', 'noisy', 'gaussian', 'genie_bound',
                      'offgrid_sbl', 'gnn', 'gamp', 'somp']
HISTORICAL_LABELS = {
    'proposed': r'Proposed ($N_{\mathrm{train}}=50\,000$)',
    'proposed_small': r'Proposed ($N_{\mathrm{train}}=5\,000$)',
    'noisy': 'LS', 'gaussian': 'Gaussian prior', 'genie_bound': 'Genie MMSE (oracle)',
    'offgrid_sbl': 'Off-grid SBL', 'gnn': 'GNN-ASPL', 'gamp': 'GAMP-SBL', 'somp': 'SOMP'}


def load_denoising(source, experiment):
    source = Path(source).resolve()
    if source.is_dir():
        source = source / 'SUMMARY.json'
    plan_path = source.parent / 'PLAN.json'
    if not plan_path.exists():
        return load(source, experiment)
    plan = read(plan_path)
    if plan.get('schema') != 'direct-awgn-existing-baselines-v1':
        return load(source, experiment)
    # This protocol is deliberately separate: "proposed" here is the pretrained
    # 50k denoiser, not the ten-layer receiver with that ID in current plans.
    summary = read(source)
    import_root = source.parents[3]
    audit_path = import_root / 'AUDIT.json'
    audit = read(audit_path)
    remote_path = import_root / 'REMOTE.json'
    remote = read(remote_path)
    if audit.get('status') != 'PASS_SAVED_RECORDS' or audit.get('curve_points') != 54:
        raise ValueError('Historical denoising needs its passing saved-record audit.')
    tree = {item['path']: item['sha'] for item in remote['tree'] if item['type'] == 'blob'}
    for path in (source, plan_path):
        raw = path.read_bytes()
        actual = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        if actual != tree[path.relative_to(import_root / 'source').as_posix()]:
            raise ValueError('Historical summary or plan differs from the imported Git snapshot.')
    if summary['status'] != 'COMPLETE' or plan['scenes'] != 500 or plan['candidates'] != 4:
        raise ValueError('Historical scene/sample identity is inconsistent.')
    expected = {(method, float(variance)) for method in HISTORICAL_METHODS for variance in plan['variances']}
    checked = {(r['method'], float(r['snr_db'])): r for r in audit['rows']}
    rows, seen = [], set()
    for saved in summary['rows']:
        row = dict(saved)
        key = row['method'], float(row['variance'])
        if key in seen or key not in expected or row['scenes'] != 500 or row['samples'] != 2000:
            raise ValueError('Historical denoising rows are missing, duplicated or unpaired.')
        seen.add(key)
        nmse = 10 * math.log10(row['error'] / row['energy'])
        snr = -10 * math.log10(row['variance'])
        audited = checked[(row['method'], float(row['snr_db']))]
        if (not math.isclose(nmse, row['nmse_db'], abs_tol=1e-10)
                or not math.isclose(snr, row['snr_db'], abs_tol=1e-10)
                or row['nmse_db'] != audited['recomputed_nmse_db']):
            raise ValueError('Historical plotting values differ from audited pooled statistics.')
        row['parameters'] = dict(variance=row['variance'], snr_db=row['snr_db'])
        row['condition'] = plan['variances'].index(row['variance'])
        rows.append(row)
    if seen != expected:
        raise ValueError('Historical denoising needs all nine curves and six conditions.')
    metadata = dict(source_summary=str(source), source_sha256=digest(source),
                    source_plan=str(plan_path), source_plan_sha256=digest(plan_path),
                    source_audit=str(audit_path), source_audit_sha256=digest(audit_path),
                    source_remote=str(remote_path), source_remote_sha256=digest(remote_path),
                    status='COMPLETE', mode='historical direct-AWGN denoising', planned_scenes=500,
                    phase_mode='not_applicable', noise_mode='known',
                    historical_protocol=plan['schema'], labels=HISTORICAL_LABELS,
                    nominal_snr_definition='-10 log10(variance), unit reference power',
                    pairing=plan['cloud_pairing'])
    return PlotData(experiment, rows, HISTORICAL_METHODS, 500, metadata)


def historical_style(method):
    if method in ('proposed', 'proposed_small'):
        selected = style.style('pretrained_first')
        if method == 'proposed_small':
            selected['color'] = '#e86d8a'
        return selected
    selected = style.style(method)
    if method == 'noisy':
        selected.update(marker='+', linestyle=':', color='#8994a3')
    elif method == 'gaussian':
        selected.update(marker='v', linestyle='--', color='#b08d26')
    elif method == 'genie_bound':
        selected.update(marker='x', linestyle='-.', color='#438b67')
    return selected


def draw_historical(data, out):
    # A taller single-column panel accommodates 5-dB ticks over the full range.
    fig, ax = style.plt.subplots(figsize=(3.5, 3.8))
    xvalues, yvalues = [], []
    handles = {}
    for method in data.methods:
        group = sorted((r for r in data.rows if r['method'] == method), key=lambda r:r['snr_db'])
        x, y = [r['snr_db'] for r in group], [r['nmse_db'] for r in group]
        handles[method], = ax.plot(x, y, label=HISTORICAL_LABELS[method], clip_on=False,
                                  zorder=4 if method.startswith('proposed') else 2,
                                  **historical_style(method))
        xvalues.extend(x); yvalues.extend(y)
    style.axes_style(ax, 'SNR (dB)', 'NMSE (dB)', xvalues)
    style.nmse_axis(ax, yvalues)
    ax.get_legend().remove()
    opts = dict(frameon=True, fancybox=False, framealpha=1, facecolor='white',
                edgecolor='#777777', handlelength=2.4, borderpad=.35, labelspacing=.25,
                handletextpad=.55, borderaxespad=.45)
    reference_opts = dict(opts, labelspacing=.15, borderaxespad=.25)
    references = ax.legend(handles=[handles[m] for m in HISTORICAL_METHODS[:5]],
                           loc='lower left', **reference_opts)
    references.get_frame().set_linewidth(.45)
    ax.add_artist(references)
    baselines = ax.legend(handles=[handles[m] for m in HISTORICAL_METHODS[5:]],
                          loc='upper right', **opts)
    baselines.get_frame().set_linewidth(.45)
    style.save(fig, out, 'channel_denoising')
    notes = [
        'Four correlated candidate channels per scene; pooled NMSE = 10 log10(sum error / sum channel energy).',
        'SNR = -10 log10(v) uses unit reference power in fixed training coordinates.',
        'The two Proposed curves are first-order denoisers trained with 5,000/50,000 channels; neither is the ten-layer receiver.',
        'Baselines retain their historical direct-denoising transfer configurations and GNN weights.',
        'Grid representation and Off-grid reconstruction limitations remain as documented in the source diagnosis.',
        'Genie is analytic conditional MMSE with true geometry, path powers and LOS gain.',
        'Cloud/local input metadata and standard-noise hashes match; truth/query hashes differ.',
        'All 54 saved NMSE values are retained; no smoothing, new inference or training.']
    return [('channel_denoising', False)], notes


def draw(data, out, args):
    if data.metadata.get('historical_protocol'):
        return draw_historical(data, out)
    fig, ax = style.plt.subplots(figsize=(3.5, 2.65))
    style.panel(ax, data, 'variance', 'Complex AWGN variance', 'nmse_db', xscale='log')
    style.save(fig, out, 'channel_denoising')
    notes = ['Configured first-network means are compared on identical known-variance AWGN queries.']
    if 'pretrained_colored_first' in data.methods:
        notes.append('The colored-trained epoch 200 EMA network is evaluated at C=vI; this is an AWGN test, not a colored-noise performance evaluation.')
    return [('channel_denoising', False)], notes


if __name__ == '__main__':
    raise SystemExit(execute('channel_denoising', draw, load_data=load_denoising))
