"""Verify the transferred first-order results and combine with local references."""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import sys

import numpy as np

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
CLOUD = OUT / 'cloud/denoising-first-20261018'
REMOTE = CLOUD / 'results/first_denoising'
LOCAL = ROOT / 'results/local_baselines_20261018/formal/channel_denoising'
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.system.observation import array_sha256


def read(path):
    return json.loads(path.read_text())


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def table(path, rows):
    with path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)))
        writer.writeheader()
        writer.writerows(rows)


def rel(path):
    return str(path.relative_to(ROOT))


def snr_db(variance):
    """SNR relative to unit channel power in the fixed training coordinates."""
    return float(-10 * np.log10(variance))


def verified_record(folder, method):
    path = folder / (method + '.json')
    row = read(path)
    assert row['status'] == 'COMPLETE' and row['samples'] == 4, path
    assert sha(path.with_suffix('.npz')) == row['compact_sha256'], path
    with np.load(path.with_suffix('.npz'), allow_pickle=False) as compact:
        for key in ('error', 'energy', 'realized_error'):
            if key not in row:
                continue
            assert np.isfinite(compact[key]).all(), path
            assert np.isclose(compact[key].sum(), row[key], rtol=1e-12, atol=1e-12), (path, key)
    return row


def main():
    frozen_before = sha(ROOT / 'MAINLINE.json')
    assets = read(OUT / 'downloads/ASSETS.json')['files']
    for name, info in assets.items():
        path = OUT / 'downloads' / name
        assert path.stat().st_size == info['bytes'] and sha(path) == info['sha256'], name
    manifest = read(CLOUD / 'MANIFEST.json')['files']
    for name, info in manifest.items():
        path = CLOUD / name
        assert path.stat().st_size == info['bytes'] and sha(path) == info['sha256'], name
    print(f'Verified {len(manifest)} exported files and all three archives.', flush=True)

    cloud_plan, local_plan = read(REMOTE / 'PLAN.json'), read(LOCAL / 'PLAN.json')
    spec, local_spec = cloud_plan['experiment'], local_plan['experiment']
    for key in ('scenes', 'seed', 'users', 'candidates', 'values', 'scale'):
        assert spec[key] == local_spec[key], key
    assert (spec['scenes'], spec['candidates']) == (500, 4)
    power_key = 'normalized_training_second_moment'
    assert spec['proposed_bundles']['proposed']['configuration']['initialization'][power_key] == local_spec['proposed_bundles']['proposed']['configuration']['initialization'][power_key]

    path_map = read(CLOUD / 'PATH_MAP.json')
    model_records = {}
    for method in ('proposed', 'proposed_small'):
        bundle = spec['proposed_bundles'][method]
        config = bundle['configuration']
        for key in ('first_checkpoint', 'prior_definition', 'completion_record'):
            requested = config[key].replace('\\', '/')
            matches = [v for k, v in path_map.items()
                       if k.replace('\\', '/') == requested or k.replace('\\', '/').endswith('/' + requested)]
            assert matches and len({v['path'] for v in matches}) == 1, requested
            mapped = matches[0]
            assert mapped['exported'] and sha(CLOUD / mapped['path']) == config[key + '_sha256']
        n = bundle['train_samples']
        complete = read(CLOUD / f'provenance/training_n{n}/complete.json')
        model_records[method] = dict(train_samples=n, label=bundle['label'],
            checkpoint=rel(CLOUD / f'weights/first_n{n}.pt'), sha256=config['first_checkpoint_sha256'],
            epochs=complete['epochs'], optimizer_steps=complete['optimizer_steps'], selected_epoch=complete['selected_epoch'])

    # Numerical thresholds are verification tolerances, not claims of bitwise pairing.
    baseline_rtol = 1e-9
    input_rtol = 1e-8
    hash_matches = dict.fromkeys(('truth_sha256', 'query_sha256', 'standard_noise_sha256'), 0)
    differences, input_checks, pairing_rows, records = {}, [], [], []
    source_hashes = {}
    refs = ('noisy', 'gaussian', 'genie_bound')
    methods = ('noisy', 'gaussian', 'proposed_small', 'proposed', 'genie_bound')
    raw = OUT / 'records'
    for scene in range(500):
        for condition, variance in enumerate(spec['values']):
            sub = Path(f'scene{scene:03d}/condition{condition:02d}')
            local_folder, cloud_folder = LOCAL / sub, REMOTE / sub
            local_input, cloud_input = read(local_folder / 'INPUT.json'), read(cloud_folder / 'INPUT.json')
            for key in ('seed', 'users', 'variance', 'scale'):
                assert local_input[key] == cloud_input[key], (sub, key)
            for key in hash_matches:
                hash_matches[key] += local_input[key] == cloud_input[key]
            assert local_input['standard_noise_sha256'] == cloud_input['standard_noise_sha256']
            pairing = dict(scene=scene, condition=condition, variance=variance, snr_db=snr_db(variance), seed=local_input['seed'], users=json.dumps(local_input['users']))
            for key in hash_matches:
                pairing['local_' + key] = local_input[key]
                pairing['cloud_' + key] = cloud_input[key]
            pairing_rows.append(pairing)
            # Only scene000 full arrays were included in the cloud export.
            if (cloud_folder / 'query.npz').exists():
                with np.load(cloud_folder / 'query.npz', allow_pickle=False) as a, np.load(local_folder / 'query.npz', allow_pickle=False) as b:
                    assert sha(local_folder / 'query.npz') == local_input['query_file_sha256']
                    for key in ('truth', 'query'):
                        assert array_sha256(a[key]) == cloud_input[key + '_sha256']
                        assert array_sha256(b[key]) == local_input[key + '_sha256']
                        delta = a[key] - b[key]
                        relative = float(np.linalg.norm(delta) / np.linalg.norm(b[key]))
                        assert relative < input_rtol, (sub, key, relative)
                        input_checks.append(dict(scene=scene, condition=condition, array=key,
                            maximum_absolute_difference=float(np.abs(delta).max()), relative_l2_difference=relative))
            destination = raw / sub
            destination.mkdir(parents=True, exist_ok=True)
            for origin, folder in (('local', local_folder), ('cloud', cloud_folder)):
                shutil.copy2(folder / 'INPUT.json', destination / f'INPUT_{origin}.json')
            cloud_records = {m: verified_record(cloud_folder, m) for m in methods}
            local_records = {m: verified_record(local_folder, m) for m in refs}
            for method in refs:
                for key in ('error', 'energy', 'realized_error'):
                    if key not in local_records[method]:
                        continue
                    a, b = cloud_records[method][key], local_records[method][key]
                    difference = abs(a-b) / abs(b)
                    label = method + '.' + key
                    differences[label] = max(differences.get(label, 0), difference)
                    assert difference < baseline_rtol, (sub, label, difference)
            for method in methods:
                origin = 'local' if method in refs else 'cloud'
                folder = local_folder if origin == 'local' else cloud_folder
                row = (local_records if origin == 'local' else cloud_records)[method]
                assert (row['scene'], row['condition'], row['method']) == (scene, condition, method)
                input_record = local_input if origin == 'local' else cloud_input
                record = dict(row, variance=variance, snr_db=snr_db(variance), origin=origin, source_json=rel(folder / (method + '.json')),
                    query_sha256=input_record['query_sha256'], truth_sha256=input_record['truth_sha256'],
                    train_samples=model_records.get(method, {}).get('train_samples'),
                    checkpoint_sha256=model_records.get(method, {}).get('sha256'))
                records.append(record)
                for suffix in ('.json', '.npz'):
                    source = folder / (method + suffix)
                    shutil.copy2(source, destination / source.name)
                    source_hashes[rel(destination / source.name)] = sha(source)
        if scene % 100 == 99:
            print(f'Validated and combined {scene + 1}/500 scenes.', flush=True)

    summaries = []
    original_summaries = {origin: read(folder / 'SUMMARY.json')['rows'] for origin, folder in [('local', LOCAL), ('cloud', REMOTE)]}
    for condition, variance in enumerate(spec['values']):
        for method in methods:
            group = [r for r in records if r['condition'] == condition and r['method'] == method]
            assert len(group) == 500
            error, energy = sum(r['error'] for r in group), sum(r['energy'] for r in group)
            row = dict(method=method, variance=variance, snr_db=snr_db(variance), origin=group[0]['origin'], scenes=500, samples=sum(r['samples'] for r in group),
                status='COMPLETE', error=error, energy=energy, nmse_db=float(10*np.log10(error/energy)),
                error_kind=group[0]['error_kind'], train_samples=group[0]['train_samples'], checkpoint_sha256=group[0]['checkpoint_sha256'])
            original = next(r for r in original_summaries[row['origin']] if r['method'] == method and r['variance'] == variance)
            assert abs(row['nmse_db']-original['nmse_db']) < 1e-10
            summaries.append(row)
    assert len(records) == 15000
    summaries.sort(key=lambda r: (r['snr_db'], methods.index(r['method'])))
    table(OUT / 'STATISTICS.csv', summaries)
    table(OUT / 'MERGED_RECORDS.csv', records)
    table(OUT / 'PAIRING.csv', pairing_rows)
    save(OUT / 'SUMMARY.json', dict(status='COMPLETE', rows=summaries, models=model_records,
        scenes=500, candidates_per_scene=4, total_records=15000, cloud_reference_records_not_counted=9000,
        scope='First-order active-channel AWGN denoising only; no second-order calibration or full receiver evaluation.',
        statistics='10 log10(sum error / sum energy); point estimates, no confidence intervals.',
        snr_axis=dict(definition_db='-10 log10(variance)', reference_power=1.0,
                      scope='Nominal denoising-input SNR in fixed normalized training coordinates; actual finite-sample channel power varies.',
                      values_db=sorted(snr_db(v) for v in spec['values'])),
        pairing='Same scene definitions, user identities and standard-noise hashes; cross-platform truth/query hashes differ. See VERIFICATION.json.'))
    save(OUT / 'VERIFICATION.json', dict(status='PASS_WITH_DOCUMENTED_CROSS_PLATFORM_INPUT_DIFFERENCES',
        archives_verified=assets, exported_files_verified=len(manifest), compact_records_verified=24000,
        input_conditions=3000, input_hash_matches=hash_matches, first_scene_array_checks=input_checks,
        input_relative_l2_tolerance=input_rtol, baseline_relative_tolerance=baseline_rtol,
        all_scene_baseline_max_relative_differences=differences,
        limitation='Cloud full query arrays are available only for scene000. Other scenes have matching metadata/noise hashes and numerically agreeing baseline errors and energies, but full-array numerical equality cannot be checked.',
        inference='Observed first-scene differences and all-scene baseline agreement are consistent with cross-platform floating-point differences; exact cause is not established.',
        local_plan_sha256=sha(LOCAL / 'PLAN.json'), cloud_plan_sha256=sha(REMOTE / 'PLAN.json'),
        frozen_mainline_sha256=frozen_before))
    save(OUT / 'RECORD_MANIFEST.json', source_hashes)
    shutil.copy2(LOCAL / 'PLAN.json', OUT / 'BASELINE_PLAN.json')
    shutil.copy2(LOCAL / 'SUMMARY.json', OUT / 'BASELINE_SUMMARY.json')

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    labels = {'noisy': 'Noisy channel', 'gaussian': 'Gaussian prior (local baseline)',
        'proposed_small': 'Proposed (5,000 training channels)', 'proposed': 'Proposed (50,000 training channels)',
        'genie_bound': 'Genie conditional MMSE (oracle)'}
    colors = {'noisy': '#777777', 'gaussian': '#ce8b00', 'proposed_small': '#2775b6', 'proposed': '#d2493d', 'genie_bound': '#299568'}
    fig, ax = plt.subplots(figsize=(8, 5.5), layout='constrained')
    for method in methods:
        rows = sorted([r for r in summaries if r['method'] == method], key=lambda r: r['snr_db'])
        ax.plot([r['snr_db'] for r in rows], [r['nmse_db'] for r in rows],
            's--' if method == 'genie_bound' else 'o-', color=colors[method], label=labels[method], linewidth=1.8)
    ax.set(xlabel='SNR (dB)', ylabel='Active-channel NMSE (dB)',
        title='First-order channel denoising\n500 physical scenes × 4 channels; known query noise')
    ax.set_xticks(sorted(snr_db(v) for v in spec['values']))
    ax.grid(alpha=.22)
    ax.legend(fontsize=9, loc='upper right')
    fig.get_layout_engine().set(rect=(0, .055, 1, .945))
    fig.text(.5, .018, r'SNR = $-10\log_{10}v$; unit reference channel power in fixed training coordinates.', ha='center', fontsize=9, color='#555555')
    for suffix in ('png', 'pdf'):
        fig.savefig(OUT / ('denoising.' + suffix), dpi=200)
    plt.close(fig)
    lines = ['一阶信道去噪合并结果（2026-10-18）', '',
        '已下载并核验 GitHub Release denoising-first-20261018 的权重、结果、源码与训练记录。',
        '合并：本地 noisy / gaussian / genie_bound，共 9,000 条；云端两个 Proposed，共 6,000 条。',
        '云端重复参考结果保留在 cloud 原始包中，不重复计数。每条曲线仍为 500 个物理场景，每场景 4 个信道。',
        'STATISTICS.csv / SUMMARY.json 为合并统计，MERGED_RECORDS.csv 为逐场景记录，records/ 保存对应原始 JSON/NPZ 副本。',
        '权重位于 cloud/denoising-first-20261018/weights/；原始源码和训练记录位于同层 provenance/。',
        '训练样本量分别为 5,000 和 50,000 个干净信道；均训练 200 轮，但更新次数不同，不能视为等计算预算实验。', '',
        '配对核验：3,000 个条件的场景种子、候选用户、噪声方差、尺度和标准噪声哈希一致。',
        'truth/query 哈希全部不同；云端仅导出了首场景的完整数组，首场景信道相对 L2 差异约 2.84e-10。',
        f'全部场景参考结果误差/能量的最大相对差异为 {max(differences.values()):.3e}。',
        '这些结果支持按相同场景设计合并展示，但不宣称跨平台输入逐字节一致；完整证据见 VERIFICATION.json 和 PAIRING.csv。', '',
        'NMSE 按误差总和/信道能量总和计算后转 dB；未平均单场景 dB。当前仅提供点估计。',
        '横轴 SNR(dB) = -10 log10(v)，采用固定训练坐标中的单位参考信道功率；档位为 -20、-10、0、10、20、30 dB。',
        '这是去噪输入的标称 SNR，有限测试集的实际平均信道功率允许有抽样偏差。原方差及条件编号保留用于数据对应。',
        'Genie 是使用真实几何、路径功率及 LOS 信息的解析条件 MMSE 参考。',
        '本批仅覆盖一阶均值去噪，不代表二阶误差校准或完整接收机性能。', '',
        'SNR(dB)   Gaussian(dB)  Proposed 5k(dB)  Proposed 50k(dB)  50k改善(dB)']
    for variance in sorted(spec['values'], reverse=True):
        d = {r['method']: r['nmse_db'] for r in summaries if r['variance'] == variance}
        lines.append(f'{snr_db(variance):<9g} {d["gaussian"]:>12.3f} {d["proposed_small"]:>16.3f} {d["proposed"]:>17.3f} {d["proposed_small"]-d["proposed"]:>12.3f}')
    lines += ['', '50k 模型在六档 SNR 上均优于 5k。SNR = -20 dB 时，5k 的 NMSE 为正且差于 Gaussian；此结果原样保留。',
        '复现合并：在项目根目录运行 .venv/bin/python results/denoising_merged_20261018/merge.py。']
    (OUT / 'REPORT.txt').write_text('\n'.join(lines) + '\n')
    assert sha(ROOT / 'MAINLINE.json') == frozen_before
    # Check copied data identities after the complete merge.
    for name, digest in source_hashes.items():
        assert sha(ROOT / name) == digest, name
    print('COMPLETE: 15,000 merged records, 30 summary rows; frozen mainline unchanged.', flush=True)


if __name__ == '__main__':
    main()
