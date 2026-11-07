"""Read frozen checkpoint shapes and verify the manuscript's network description.

CPU-only synthetic shape checks; no training or receiver performance experiment.
"""
from pathlib import Path
import hashlib
import json
import sys

import torch

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'src'))
from training.colored_preconditioned_20261024.model import load_checkpoint
from algorithm.STMP.activity import Config, EvidenceNetwork

torch.set_num_threads(2)
torch.manual_seed(0)
cfg = json.loads((ROOT / 'src/configs/candidates/C_STMP_variance_em_20261025.json').read_text())
record = {'scope': 'checkpoint identity, architecture, and synthetic CPU tensor shapes only'}
for key in ('first_checkpoint', 'evidence_checkpoint'):
    path = ROOT / cfg[key]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest == cfg[key + '_sha256']
    record[key] = {'path': cfg[key], 'sha256': digest}

model, first = load_checkpoint(ROOT / cfg['first_checkpoint'], 'cpu')
trunk = model.backbone.trunk
record['denoiser_config'] = first['config']
record['conditioning_linear_shapes'] = [
    [m.in_features, m.out_features] for m in model.backbone.condition if isinstance(m, torch.nn.Linear)
]
assert record['conditioning_linear_shapes'] == [[1025, 64], [64, 64]]
shapes = {}
hooks = []
for name in ('begin_conv', 'refine1', 'refine2', 'refine3', 'refine4', 'end_conv'):
    hooks.append(getattr(trunk, name).register_forward_hook(
        lambda _m, _i, out, name=name: shapes.update({name: list(out.shape)})))
for i in range(1, 5):
    stage = getattr(trunk, f'res{i}')
    assert len(stage) == 2
    hooks.append(stage[-1].register_forward_hook(
        lambda _m, _i, out, name=f'res{i}': shapes.update({name: list(out.shape)})))
with torch.inference_mode():
    condition = model.backbone.condition(torch.zeros(1, 1025))
    output = trunk(torch.zeros(1, 32, 16, 16), condition)
assert torch.isfinite(output).all()
expected = {
    'begin_conv': [1, 128, 16, 16], 'res1': [1, 128, 16, 16],
    'res2': [1, 256, 8, 8], 'res3': [1, 256, 8, 8], 'res4': [1, 256, 8, 8],
    'refine1': [1, 256, 8, 8], 'refine2': [1, 256, 8, 8],
    'refine3': [1, 128, 8, 8], 'refine4': [1, 128, 16, 16], 'end_conv': [1, 32, 16, 16],
}
assert shapes == expected, shapes
record['denoiser_shapes'] = shapes
for hook in hooks:
    hook.remove()

blob = torch.load(ROOT / cfg['evidence_checkpoint'], map_location='cpu', weights_only=False)
net = EvidenceNetwork(Config(**blob['config'])).eval()
net.load_state_dict(blob['state_dict'], strict=True)
record['classifier_config'] = blob['config']
record['classifier_convolutions'] = [
    {'in': m.in_channels, 'out': m.out_channels, 'kernel': list(m.kernel_size),
     'stride': list(m.stride), 'padding': list(m.padding)}
    for m in net.modules() if isinstance(m, torch.nn.Conv2d)
]
assert [x['out'] for x in record['classifier_convolutions']] == [64, 64, 128, 128, 128, 128]
assert [x['stride'] for x in record['classifier_convolutions']] == [[1, 1], [1, 1], [2, 2], [1, 1], [2, 2], [1, 1]]
assert net.readout[0].in_features == 2053
assert net.readout[0].out_features == 128 and net.readout[2].out_features == 1
with torch.inference_mode():
    output = net(torch.zeros(1, 2, 16, 16, 16), torch.ones(1), torch.zeros(1, 2, 16, 16, 16))
assert list(output.shape) == [1] and torch.isfinite(output).all()
record['classifier_readout_widths'] = [2053, 128, 1]
record['status'] = 'PASS'
Path(__file__).with_name('ARCHITECTURE_CHECK.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
print('PASS: frozen weights, denoiser stages, classifier layers, and synthetic tensor shapes.')
