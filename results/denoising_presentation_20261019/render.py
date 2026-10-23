"""Render the canonical independent-denoising figure and verify its data."""
from pathlib import Path
import csv
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
import render_experiment_figures as render

OUT = ROOT / 'results/denoising_four_baselines_20261018'
DATA = ['SUMMARY.json', 'STATISTICS.csv', 'SNR_NMSE.csv']
def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

before = {name: sha(OUT / name) for name in DATA}
summary = json.loads((OUT / 'SUMMARY.json').read_text())
assert summary['status'] == 'COMPLETE' and len(summary['rows']) == 54
mapping = {'LS': 'noisy', 'Gaussian': 'gaussian', 'SOMP': 'somp', 'GAMP-SBL': 'gamp',
           'GNN-ASPL': 'gnn', 'Off-grid SBL': 'offgrid_sbl', 'Proposed 5k': 'proposed_small',
           'Proposed 50k': 'proposed', 'Genie MMSE': 'genie_bound'}
lookup = {(float(r['snr_db']), r['method']): r for r in summary['rows']}
checked = 0
with (OUT / 'SNR_NMSE.csv').open() as file:
    for row in csv.DictReader(file):
        for label, method in mapping.items():
            ref = lookup[(float(row['snr_db']), method)]
            assert ref['scenes'] == 500 and ref['samples'] == 2000
            assert abs(float(row[label]) - ref['nmse_db']) < 1e-12
            checked += 1
assert checked == 54
render.setup()
render.denoising('channel_denoising', 'results/denoising_four_baselines_20261018')
assert before == {name: sha(OUT / name) for name in DATA}
manifest_path = render.OUT / 'FIGURES.json'
manifest = json.loads(manifest_path.read_text())
variants = {'channel_denoising', 'channel_denoising_main', 'channel_denoising_training',
            'channel_denoising_references', 'denoising_diagnosis'}
manifest['figures'] = [f for f in manifest['figures'] if f['name'] not in variants] + render.FIGURES
manifest['renderer_sha256'] = sha(ROOT / 'scripts/render_experiment_figures.py')
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
verification = {'status': 'PASS', 'figure': 'denoising.png', 'vector_figure': 'denoising.pdf',
    'methods': mapping, 'snr_points': 6, 'verified_nmse_values': checked,
    'physical_scenes_per_condition': 500, 'channels_per_scene': 4,
    'source_statistics_unchanged': True, 'data_sha256': before,
    'figure_sha256': {name: sha(OUT / name) for name in ['denoising.png', 'denoising.pdf']},
    'renderer': 'scripts/render_experiment_figures.py'}
(OUT / 'PRESENTATION.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({'status': 'PASS', 'verified_nmse_values': checked, 'directory': str(OUT)}))
