"""Export trained joint denoisers and their frozen base bank as a portable bundle."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from afdm_jadcedd.utils import sha256, write_json


def export(manifest, output):
    manifest, output = Path(manifest), Path(output)
    spec = json.loads(manifest.read_text())
    if spec['schema'] != 'public-variance-selected-dncnn-v1':
        raise ValueError('Expected the development range-selection manifest')
    payloads = {}
    sources = {}
    for kind in ('low', 'high'):
        path = Path(spec[kind]['path'])
        if not path.is_absolute():
            path = manifest.parent / path
        if sha256(path) != spec[kind]['sha256']:
            raise ValueError('Development checkpoint changed')
        # These are local, hash-verified training checkpoints. The exported
        # inference bundle contains only tensors and ordinary Python values.
        payloads[kind] = torch.load(path, map_location='cpu', weights_only=False)
        sources[kind] = dict(path=str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
                             sha256=sha256(path))
    low, high = payloads['low'], payloads['high']
    if low['schema'] != 'noise-scaled-frozen-beam-plus-learned-joint-correction-v1':
        raise ValueError('Expected noise-scaled residual checkpoint')
    if high['mode'] != 'moment_skip' or low['scale'] != high['scale']:
        raise ValueError('Incompatible trained denoisers')
    bank = Path(low['plan']['bank_path'])
    if sha256(bank / 'BANK.json') != low['plan']['bank_sha256']:
        raise ValueError('Base bank identity mismatch')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'base').mkdir()
    bank_spec = json.loads((bank / 'BANK.json').read_text())
    shutil.copy2(bank / 'BANK.json', output / 'base/BANK.json')
    for entry in bank_spec['entries']:
        path = bank / entry['path']
        if sha256(path) != entry['sha256']:
            raise ValueError('Base checkpoint identity mismatch')
        shutil.copy2(path, output / 'base' / entry['path'])
    result = dict(schema='afdm-joint-dncnn-bundle-v1', scale=float(low['scale']),
                  boundary=spec['boundary'], selection_scope=spec['selection_scope'],
                  base=dict(path='base/BANK.json', sha256=sha256(output / 'base/BANK.json')),
                  training_sources=sources, selection_manifest_sha256=sha256(manifest))
    for kind, payload in payloads.items():
        # Retain the embedded frozen bank so the loader can prove that the
        # residual training never changed its weights or running statistics.
        exported = dict(model={k: v.cpu() for k, v in payload['model'].items()},
                        power=torch.as_tensor(payload['power']).tolist(),
                        width=int(payload['width']), depth=int(payload['depth']),
                        scale=float(payload['scale']))
        if kind == 'high':
            exported['mode'] = payload['mode']
        torch.save(exported, output / f'{kind}.pt')
        result[kind] = dict(path=f'{kind}.pt', sha256=sha256(output / f'{kind}.pt'))
    write_json(output / 'BUNDLE.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    print(json.dumps(export(args.manifest, args.output), indent=2))
