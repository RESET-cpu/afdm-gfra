"""Read audited historical denoising summaries; no inference implementation."""

from pathlib import Path

import hashlib

import math

from plotting.data import PlotData, digest, load, read

from plotting import style

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

METHOD = 'pretrained_colored_first'

def load_append(source, experiment):
    source = Path(source).resolve()
    if source.is_dir():
        source = source/'SUMMARY.json'
    plan_path = source.parent/'PLAN.json'
    plan, summary = read(plan_path), read(source)
    audit_path = source.parent/'VERIFICATION.json'
    audit = read(audit_path)
    if (plan.get('schema') != 'direct-awgn-colored-append-v1'
            or plan['scene_count'] != 500 or summary['status'] != 'COMPLETE'
            or audit['status'] != 'PASS' or audit['paired_input_conditions'] != 3000
            or not audit['original_54_rows_unchanged']
            or summary['source_plan_sha256'] != digest(plan_path)
            or audit['new_summary_sha256'] != digest(source)):
        raise ValueError('A complete verified 500-scene append is required')
    original = Path(plan['source_summary'])
    if digest(original) != plan['source_summary_sha256']:
        raise ValueError('Original summary changed')
    old = load_denoising(original, experiment)
    if summary['rows'][:54] != read(original)['rows'] or len(summary['rows']) != 60:
        raise ValueError('The original 54 points must remain unchanged')
    rows = list(old.rows)
    seen = set()
    for saved in summary['rows'][54:]:
        row = dict(saved)
        variance = row['variance']
        if (row['method'] != METHOD or variance in seen or variance not in plan['variances']
                or row['scenes'] != 500 or row['samples'] != 2000
                or not math.isclose(10*math.log10(row['error']/row['energy']), row['nmse_db'], abs_tol=1e-10)
                or not math.isclose(-10*math.log10(variance), row['snr_db'], abs_tol=1e-10)):
            raise ValueError('Appended curve identity or pooled metric differs')
        seen.add(variance)
        row.update(parameters=dict(variance=variance, snr_db=row['snr_db']),
                   condition=plan['variances'].index(variance))
        rows.append(row)
    metadata = dict(old.metadata, source_summary=str(source), source_sha256=digest(source),
                    source_plan=str(plan_path), source_plan_sha256=digest(plan_path),
                    source_audit=str(audit_path), source_audit_sha256=digest(audit_path),
                    original_summary=str(original), original_summary_sha256=digest(original),
                    mode='historical 500-scene AWGN comparison with one appended first network',
                    appended_pairing=plan['pairing'],
                    labels=dict(HISTORICAL_LABELS, **{METHOD: 'Colored-trained score'}))
    return PlotData(experiment, rows, [*HISTORICAL_METHODS[:2], METHOD, *HISTORICAL_METHODS[2:]], 500, metadata)
