"""Check frozen training data, source snapshots, selection and exported weights."""
import json
from pathlib import Path
import sys
import numpy as np
import torch
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from afdm_jadcedd.utils import sha256,write_json
from afdm_jadcedd.algorithm.baselines.ldamp.representation import Representation,beam_transform
from afdm_jadcedd.algorithm.baselines.ldamp_joint.denoiser import verify_bundle


def main():
    root=ROOT/'results/ldamp_complete_20261015';cache=root/'cache'
    manifest=json.loads((cache/'MANIFEST.json').read_text());checks=[]
    def check(name,passed,**evidence):
        checks.append(dict(name=name,passed=bool(passed),**evidence))
    identities={}
    for split in ['train','validation']:
        source=ROOT/f'data/proposed/{split}_channel.npy';cached=cache/f'{split}.npy'
        expected=manifest['data'][split]
        check(split+'_source_hash',sha256(source)==expected['source_sha256'],sha256=sha256(source))
        check(split+'_cache_hash',sha256(cached)==expected['cache_sha256'],sha256=sha256(cached))
        original=np.load(source,mmap_mode='r');transformed=np.load(cached,mmap_mode='r')
        identities[split]=np.load(ROOT/f'data/proposed/{split}_identities.npy')
        check(split+'_full_dimensions',original.shape==transformed.shape==(expected['users'],16,16,16))
        indices=np.random.default_rng(202610150401).choice(len(original),size=32,replace=False)
        reference=Representation().forward(beam_transform(original[indices]/manifest['scale'])).astype(np.complex64)
        actual=transformed[indices]
        check(split+'_sampled_transform',np.array_equal(reference,actual),users=32,
            max_absolute_difference=float(np.max(abs(reference-actual))))
    check('physical_train_validation_disjoint',not np.intersect1d(identities['train'][:,0],identities['validation'][:,0]).size)
    profile_path=ROOT/manifest['profiles_source'];profiles=json.loads(profile_path.read_text())
    check('profile_source_hash',sha256(profile_path)==manifest['profiles_sha256'])
    check('profile_cache_matches_source',np.array_equal(np.load(cache/'profiles.npy'),np.array([r['relative_variance'] for r in profiles['rows']])))
    training=[]
    for name in ['moment_skip','moment_refine_lr1e3','residual_noise']:
        folder=root/name;payload=torch.load(folder/'best.pt',map_location='cpu',weights_only=False)
        plan=json.loads((folder/'PLAN.json').read_text());history=json.loads((folder/'HISTORY.json').read_text())
        status=json.loads((folder/'STATUS.json').read_text());best=min(history,key=lambda r:r['metrics']['selection_score'])
        check(name+'_completed',status['status']=='COMPLETE' and history[-1]['step']==plan['steps'])
        check(name+'_best_selection',payload['step']==best['step'] and payload['metrics']==best['metrics'])
        for source,digest in plan['source_sha256'].items():
            check(name+'_source_'+source,sha256(folder/'sources'/source)==digest)
        data_key=next(k for k in ['cache_manifest_sha256','data_manifest_sha256'] if k in plan)
        check(name+'_data_binding',plan[data_key]==sha256(cache/'MANIFEST.json'))
        if 'initial_checkpoint' in plan:
            path=Path(plan['initial_checkpoint']);path=path if path.is_absolute() else ROOT/path
            check(name+'_initialization',sha256(path)==plan['initial_sha256'])
        training.append(dict(name=name,checkpoint_sha256=sha256(folder/'best.pt'),steps_completed=history[-1]['step'],
            selected_step=best['step'],best_score=best['metrics']['selection_score'],seed=plan['seed'],
            validation_band_ratios=[r['error_over_zero'] for r in best['metrics']['rows']]))
    bundle_path=ROOT/'models/ldamp_joint/v1/BUNDLE.json';bundle=verify_bundle(bundle_path)
    for kind in ['low','high']:
        origin=bundle['training_sources'][kind];path=ROOT/origin['path']
        check(kind+'_source_checkpoint_hash',sha256(path)==origin['sha256'])
        raw=torch.load(path,map_location='cpu',weights_only=False)
        exported=torch.load(bundle_path.parent/bundle[kind]['path'],map_location='cpu',weights_only=True)
        check(kind+'_export_exact_tensors',raw['model'].keys()==exported['model'].keys() and
            all(torch.equal(raw['model'][k],exported['model'][k]) for k in raw['model']))
        check(kind+'_export_architecture',all(raw[k]==exported[k] for k in ['width','depth','scale']))
    selected=root/'range_selection_mean_and_beam/residual_noise.json'
    check('range_rule_source',sha256(selected)==bundle['selection_manifest_sha256'])
    report=json.loads((root/'range_selection_mean_and_beam/SUMMARY.json').read_text())
    check('selected_low_model',report['selected']=='residual_noise')
    check('all_six_selected_denoising_bands_reported',len(report['metrics']['rows'])==6)
    result=dict(status='PASS' if all(c['passed'] for c in checks) else 'FAILED',checks=checks,training=training,
        selected_denoising_band_ratios=[r['error_over_zero'] for r in report['metrics']['rows']],
        bundle_sha256=sha256(bundle_path),script_sha256=sha256(Path(__file__)),
        scope='Data hashes, saved training source snapshots, checkpoint selection and exported tensors. Does not re-run training or claim cross-hardware bitwise training reproducibility.')
    write_json(root/'TRAINING_PROVENANCE_AUDIT.json',result)
    print(json.dumps(dict(status=result['status'],checks=len(checks),failures=[c for c in checks if not c['passed']],training=training),indent=2))
    return 0 if result['status']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
