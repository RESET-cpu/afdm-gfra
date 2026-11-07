"""Prepare the shared test-scene registry; no observations or inference are run."""
from pathlib import Path
import argparse
import csv
import hashlib
import json


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / 'results/lstmp_v3_shared2000_20261021'
TRAIN = Path(r'D:\afdm-gfra-cpu\runs\lstmp_conditional_bce_v3_depth10_fast_20261020')
COUNT = 2000
BASE_SEED = 202610219100001
PANEL_ID = 'lstmp_v3_shared2000_20261021'
DEFAULT = dict(users=40, frames=16, activity_probability=.1, snr_db=0,
               channel_model='D', pilot='dft')
SWEEPS = {
    'snr_comparison': ('snr_db', [-4, -2, 0, 2, 4, 6]),
    'pilot_frames': ('frames', [8, 16, 24, 32, 40, 48]),
    'user_count': ('users', [20, 40, 60, 80, 100]),
    'activity_probability': ('activity_probability', [.05, .1, .15, .2, .25]),
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write('\n')


def condition_key(parameters):
    """An input key is independent of experiment name and receiver method."""
    p = dict(DEFAULT, **parameters)
    return (f"K{int(p['users'])}_Q{int(p['frames'])}_p{p['activity_probability']:g}"
            f"_snr{p['snr_db']:g}_{p['channel_model']}_{p['pilot']}")


def scene_rows():
    return [dict(index=i, scene_id=f'scene{i:04d}', seed=BASE_SEED+i)
            for i in range(COUNT)]


def experiment_specs():
    common = dict(scenes=COUNT, scene_registry='SCENES.csv',
                  selection=dict(start=0, stop_exclusive=COUNT), base_seed=BASE_SEED)
    specs = {}
    for name, (field, values) in SWEEPS.items():
        conditions = [dict(DEFAULT, **{field: value}) for value in values]
        specs[name] = dict(common, variable=field, values=values,
                          conditions=conditions,
                          input_condition_keys=[condition_key(p) for p in conditions])
    profiles = [dict(DEFAULT, channel_model=profile, snr_db=snr)
                for profile in ['D', 'A', 'B', 'C'] for snr in SWEEPS['snr_comparison'][1]]
    specs['cross_channel'] = dict(common, profiles=['D', 'A', 'B', 'C'],
        snr_db=SWEEPS['snr_comparison'][1], conditions=profiles,
        input_condition_keys=[condition_key(p) for p in profiles])
    specs['channel_denoising'] = dict(common, users=40, candidates_per_scene=4,
        values=[.001, .01, .1, 1., 10., 100.],
        independent_scene_count=COUNT, queries_per_noise_variance=COUNT*4,
        noise_mode='known_awgn', module_scope='Pretrained channel prior; not the full ten-layer receiver')
    specs['density_ratio_ablation'] = dict(common,
        status='AWAITING_NEW_ARCHITECTURE_CONTRAST_DEFINITION',
        legacy_snr_reference=[-4, -2, 0, 2, 4, 6, 8],
        executable=False, note='Scene sharing and count confirmed; old three-network ablation is not relabeled as a ten-layer ablation.')
    specs['convergence'] = dict(common, scenes=20,
        selection=dict(start=0, stop_exclusive=20), snr_db=[-4, 0, 4],
        pilots=['dft', 'hadamard'], note='Original 20-scene size retained; predetermined prefix of the shared registry.')
    return specs


def separation_audit():
    """Read metadata only; the training receipt records earlier receiver ranges."""
    evidence = []
    for name in ['receiver_train.json', 'receiver_validation.json']:
        path = TRAIN / 'data' / name
        identity = read(path)['identity']
        evidence.append(dict(source=str(path), sha256=sha(path),
            begin=identity['base_seed'], end_exclusive=identity['base_seed']+identity['count']))
    path = TRAIN / 'protocol/SEED_SEPARATION.json'
    previous = read(path)
    for row in previous['previous_receiver_receipts']:
        evidence.append(dict(source=row['receipt'], begin=row['begin'], end_exclusive=row['end_exclusive']))
    # Check the revealed receiver panels and the historical experiment seed ranges.
    for name in ['lstmp_v3_depth10_previous20_20261020', 'lstmp_v3_depth10_standard20_gpu_20261021']:
        path = ROOT / 'results' / name / 'PLAN.json'
        seeds = [case['seed'] for case in read(path)['cases']]
        evidence.append(dict(source=str(path), sha256=sha(path),
            begin=min(seeds), end_exclusive=max(seeds)+1))
    for name, begin in [('historical_snr', 202610172000001),
                        ('pilot_frames', 202610180100001), ('user_count', 202610180200001),
                        ('activity_probability', 202610180300001), ('convergence', 202610180400001),
                        ('channel_denoising', 202610180500001), ('cross_channel', 202610180600001)]:
        evidence.append(dict(source='Existing experiment entry: '+name, begin=begin,
                             end_exclusive=begin+(20 if name=='convergence' else 500)))
    for row in evidence:
        if max(BASE_SEED, row['begin']) < min(BASE_SEED+COUNT, row['end_exclusive']):
            raise ValueError('Test seeds overlap: '+row['source'])
    return dict(status='PASSED_FOR_LISTED_RECEIVER_RANGES', checked_ranges=evidence,
        boundary='This is seed identity checking, not a proof of statistical independence or a complete audit of every baseline training bank. Full model/data bindings remain part of execution preparation.')


def prepare():
    if OUTPUT.exists():
        raise FileExistsError('Registry already exists; use --inspect: '+str(OUTPUT))
    specs = experiment_specs()
    keys = {key for name in SWEEPS for key in specs[name]['input_condition_keys']}
    assert len(keys)==19
    audit = separation_audit()
    complete = read(TRAIN / 'COMPLETE.json')
    plan = dict(schema='afdm-shared-test-panel-v1', panel_id=PANEL_ID,
        status='SCENE_POLICY_FIXED_EXECUTION_ADAPTATION_PENDING',
        material_passport=dict(origin_skill='academic-research-suite / experiment-agent',
            origin_mode='plan', origin_date='2026-10-21', verification_status='UNVERIFIED',
            version_label='shared_scene_plan_v1'),
        authorization='User confirmed: replace the former 500-scene tests with 2000 shared physical scene identities.',
        scene_count=COUNT, base_seed=BASE_SEED, last_seed=BASE_SEED+COUNT-1,
        independent_unit='physical_scene_id', observations_generated=0, inferences_completed=0,
        defaults=DEFAULT, phase_mode='estimated', noise_mode='estimated',
        new_model=dict(checkpoint=complete['selected_checkpoint'], sha256=complete['selected_sha256'],
                       depth=10, selected_epoch=1, activity_threshold=.5),
        experiments=specs,
        unique_conditions_in_four_primary_sweeps=len(keys),
        scene_condition_pairs_in_four_primary_sweeps=COUNT*len(keys),
        reuse=dict(input_key='{panel_id}/{scene_id}/{condition_key}',
            same_condition='Reuse identical observation, truth and valid frontend cache across methods and experiments.',
            changed_condition='Rebuild the appropriate observation; retain matched geometry and random streams where the physical model allows.',
            result_key='Input identity plus algorithm, weights, inference controls and execution identity; never method name alone.',
            performance_reuse='Only after input/model/config/source hashes match.',
            timing='Historical cached inference times do not count as newly measured timing; observer overhead is excluded.'),
        statistics=dict(bootstrap_replicates=10000, unit='physical_scene_id',
            shared_indices_across_methods_conditions_and_experiments=True,
            note='Shared experiments and the four denoising queries are not additional independent replications.'),
        execution_entrypoint=None,
        remaining_work=['Ten-layer integration into the full experiment runner',
                        'Full model/data identity and seed audit',
                        'Freeze physical input generation and cache bindings',
                        'Define ablations appropriate to the new architecture'])
    OUTPUT.mkdir(parents=True)
    with (OUTPUT/'SCENES.csv').open('x', encoding='utf-8', newline='') as stream:
        writer=csv.DictWriter(stream, fieldnames=['index','scene_id','seed'])
        writer.writeheader(); writer.writerows(scene_rows())
    plan['scene_registry_sha256']=sha(OUTPUT/'SCENES.csv')
    plan['preparation_source_sha256']=sha(__file__)
    save(OUTPUT/'PLAN.json', plan)
    save(OUTPUT/'SEED_SEPARATION.json', audit)
    save(OUTPUT/'MANIFEST.json', {name:sha(OUTPUT/name) for name in
                                 ['PLAN.json','SCENES.csv','SEED_SEPARATION.json']})
    inspect()


def inspect():
    for name, digest in read(OUTPUT/'MANIFEST.json').items():
        assert sha(OUTPUT/name)==digest, name
    plan=read(OUTPUT/'PLAN.json')
    with (OUTPUT/'SCENES.csv').open(encoding='utf-8', newline='') as stream:
        rows=list(csv.DictReader(stream))
    assert len(rows)==COUNT and [int(row['seed']) for row in rows]==list(range(BASE_SEED, BASE_SEED+COUNT))
    assert len({row['scene_id'] for row in rows})==COUNT
    assert sha(OUTPUT/'SCENES.csv')==plan['scene_registry_sha256']
    print(json.dumps(dict(status=plan['status'], scenes=COUNT,
        experiments={k:v['scenes'] for k,v in plan['experiments'].items()},
        unique_primary_conditions=19, scene_condition_pairs=19*COUNT,
        observations_generated=0, inferences_completed=0), ensure_ascii=False))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--prepare',action='store_true')
    mode.add_argument('--inspect',action='store_true')
    args=parser.parse_args()
    prepare() if args.prepare else inspect()
