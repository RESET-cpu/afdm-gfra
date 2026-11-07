"""Prepare an explicit local migration manifest; never run experiments."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / 'result'
RECORD = ROOT / 'paper/docs/result_layout_20261023'
ARCHIVE = ROOT / 'archive/result_legacy_20261023'
NAMES = ['snr_comparison', 'pilot_frames', 'user_count', 'activity_probability',
         'cross_channel', 'channel_denoising', 'runtime_comparison', 'density_ratio_ablation']
PROTECTED = {'main2000_known_phase_20261023', 'lstmp_v3_shared2000_20261021', 'models', 'runs', 'data'}
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
assert ROOT == Path('D:/afdm-gfra')
assert not ARCHIVE.exists()
assert not any((RESULT / n).exists() for n in NAMES)
assert not RECORD.exists()
RECORD.mkdir(parents=True)
original = sorted(p for p in RESULT.iterdir() if p.is_dir())
plan_path = RESULT / 'main2000_known_phase_20261023/snr_comparison_passive/PLAN.json'
plan = json.loads(plan_path.read_text(encoding='utf-8'))
for p, expected in plan['assets'].items():
    assert sha(Path(p)) == expected, p
moves = []
for source in original:
    if source.name in PROTECTED:
        continue
    destination = (RESULT / 'channel_denoising/data/imports') if source.name == 'imports' else ARCHIVE / source.name
    moves.append(dict(source=str(source), destination=str(destination),
                      kind='result_directory', directory_id=source.stat().st_ino,
                      hidden_compatibility=True))
figure_manifest = []
paper_figures = ROOT / 'paper/TWC-1/figures'
for source in sorted(paper_figures.iterdir()):
    if not source.is_dir():
        continue
    experiment = 'snr_comparison' if source.name.startswith('stmp_known_phase_') else 'channel_denoising' if source.name.startswith('denoising_') else None
    if experiment is None:
        continue
    destination = RESULT / experiment / 'figures' / source.name
    moves.append(dict(source=str(source), destination=str(destination), kind='figure_directory',
                      directory_id=source.stat().st_ino, hidden_compatibility=False))
    for p in sorted(source.rglob('*')):
        if p.is_file():
            figure_manifest.append(dict(old=str(p), new=str(destination/p.relative_to(source)), sha256=sha(p)))
links = []
def link(experiment, name, target, status):
    assert target.exists(), target
    links.append(dict(path=str(RESULT/experiment/'data'/name), target=str(target), status=status))
link('snr_comparison', 'current', plan_path.parent, 'RUNNING_KNOWN_PHASE_ESTIMATED_NOISE')
link('snr_comparison', 'shared', RESULT/'main2000_known_phase_20261023/shared', 'SHARED_INPUTS')
link('snr_comparison', 'scene_registry', RESULT/'lstmp_v3_shared2000_20261021', 'FROZEN_2000_SCENES')
for stamp, count in [('20261023_154730',193), ('20261023_180346',500)]:
    link('snr_comparison', f'interim_{count}', RESULT/f'main2000_known_phase_20261023/progress_snapshots/{stamp}', f'AUDITED_INTERIM_{count}')
for batch in original:
    if batch.name in PROTECTED or batch.name == 'imports':
        continue
    for name in NAMES:
        target = batch / name
        if not target.is_dir():
            continue
        if batch.name == 'main2000_initialization_runtime_20261023':
            link(name, 'planned_2000_ten_layer', target, 'PLANNED_NOT_STARTED' if name!='density_ratio_ablation' else 'DEFERRED_BY_USER')
            continue
        summary = target/'SUMMARY.json'
        status = json.loads(summary.read_text(encoding='utf-8-sig')).get('status','HISTORICAL') if summary.exists() else 'HISTORICAL_PLAN_OR_PARTIAL_RESULTS'
        link(name, 'history/'+batch.name, target, status)
link('snr_comparison', 'history/baseline_comparison_500_20261018', RESULT/'baseline_comparison_500_20261018', 'HISTORICAL_COMPLETE_DIFFERENT_PROTOCOL')
link('channel_denoising', 'current', RESULT/'imports/denoising_mac_20261023_4173ccc/source/results/denoising_four_baselines_20261018', 'COMPLETE_500_SCENES_9_CURVES')
first = RESULT/'runs/proposed_50000_cuda_graph_20261018/first_denoising'
if first.exists():
    link('channel_denoising', 'history/proposed_first_500_20261018', first, 'HISTORICAL_SOURCE_RESULTS')
before = RECORD/'before'
before.mkdir()
for path in [RESULT/'README.md', ROOT/'README.md', ROOT/'src/evaluation/plots/README.md',
             ROOT/'paper/TWC-1/README.md', ROOT/'paper/TWC-1/figures/README.md']:
    out = before / path.relative_to(ROOT)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(path.read_bytes())
manifest = dict(status='PREPARED', created_utc=datetime.now(timezone.utc).isoformat(),
    root=str(ROOT), archive=str(ARCHIVE), experiments=NAMES,
    protected_original_directories=[str(RESULT/n) for n in sorted(PROTECTED)],
    original_top_directories=[dict(path=str(p),attributes=p.stat().st_file_attributes,directory_id=p.stat().st_ino) for p in original],
    moves=moves, data_links=links, figure_files=figure_manifest,
    active_plan=str(plan_path), active_plan_sha256=sha(plan_path), frozen_assets=plan['assets'],
    current_status_before=json.loads((plan_path.parent/'STATUS.json').read_text()),
    policy='Eight visible experiment folders; hidden compatibility paths preserve ongoing execution and frozen references. No data deletion, inference, training, or frozen source edits.')
(RECORD/'PLAN.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(dict(moves=len(moves),data_links=len(links),figure_files=len(figure_manifest),frozen_assets=len(plan['assets']),record=str(RECORD))))
