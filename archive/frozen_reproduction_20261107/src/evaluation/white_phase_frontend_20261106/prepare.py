"""Freeze a separate plan and paired references without running inference."""
import shutil
import time
from pathlib import Path
from .common import OUT, WHITE, COLORED, ABLATION, PACKAGE, BINDING, ROOT, SNRS, checked, tag, verify
from utils import read_json, write_json, sha256


def prepare():
    if (OUT/'PLAN.json').exists():
        return verify()
    request = read_json(OUT/'REQUEST.json')
    for path, digest in request['assets'].items():
        checked(ROOT/path, digest)
    white_plan, colored_plan = read_json(WHITE/'PLAN.json'), read_json(COLORED/'PLAN.json')
    complete = read_json(WHITE/'COMPLETION.json')
    assert complete['status'] == 'PASS'
    checked(WHITE/'SUMMARY.json', complete['summary_sha256'])
    checked(WHITE/'PAIRED_CASES.csv', complete['paired_sha256'])
    binding = read_json(BINDING)
    config = read_json(ROOT/binding['receiver_configuration'])
    assert config == white_plan['receiver_configuration']
    for key in ('receiver_configuration', 'phase_configuration', 'initializer_source'):
        checked(ROOT/binding[key], binding[key+'_sha256'])
    original = read_json(colored_plan['configuration'])
    assert {k:v for k,v in binding.items() if not k.startswith('receiver_configuration')} == {
        k:v for k,v in original.items() if not k.startswith('receiver_configuration')}
    cases = read_json(WHITE/'INPUTS.json')
    assert cases == read_json(COLORED/'INPUTS.json') and len(cases) == 6000
    references = []
    for position, case in enumerate(cases):
        assert (case['scene'], case['index'], case['snr_db']) == (position//6, position%6, SNRS[position%6])
        reference = dict(scene=case['scene'], index=case['index'], snr_db=case['snr_db'])
        for label, source, hash_key in (('white_known_phase', WHITE, 'sha256'),
                                         ('colored_estimated_phase', COLORED, 'result_sha256')):
            pointer = source/'results'/(tag(position)+'.json')
            link = read_json(pointer)
            checked(link['result'], link[hash_key])
            row = read_json(link['result'])
            assert row['input_files'] == case['files']
            assert (row['scene'], row['index'], row['snr_db']) == (case['scene'], case['index'], case['snr_db'])
            reference[label] = dict(pointer=str(pointer), pointer_sha256=sha256(pointer),
                                    result=link['result'], result_sha256=link[hash_key])
        references.append(reference)
        if (position+1) % 1000 == 0:
            print(dict(stage='REFERENCE_METADATA', checked=position+1), flush=True)
    for name, value in (('INPUTS.json', cases), ('REFERENCES.json', references)):
        path = OUT/name
        if path.exists():
            assert read_json(path) == value
        else:
            write_json(path, value)
    assets = {}
    for previous in (white_plan, colored_plan):
        for path, digest in previous['assets'].items():
            if '/src/' in Path(path).as_posix() and Path(path).suffix == '.py':
                checked(path, digest)
                assert path not in assets or assets[path] == digest
                assets[path] = digest
    paths = [OUT/n for n in ('REQUEST.json', 'INPUTS.json', 'REFERENCES.json')]
    paths += list(PACKAGE.glob('*.py')) + [BINDING, ROOT/binding['receiver_configuration'],
              ROOT/binding['phase_configuration'], ROOT/binding['initializer_source'], ABLATION/'PLAN.json']
    for folder in (WHITE, COLORED):
        paths += [folder/n for n in ('PLAN.json', 'PLAN_HASH.json', 'COMPLETION.json', 'SUMMARY.json')]
    for key, value in config.items():
        if key.endswith('_sha256') and key[:-7] in config and isinstance(config[key[:-7]], str):
            path = ROOT/config[key[:-7]]
            checked(path, value)
            paths.append(path)
    assets.update({str(path.resolve()): sha256(path) for path in paths})
    worker_assets = {path:digest for path,digest in assets.items()
                     if '/src/' in Path(path).as_posix() or path in (str(OUT/'INPUTS.json'), str(OUT/'REFERENCES.json'))}
    native = Path(request['native_directory'])
    assert not native.exists(), 'Existing native results require inspection; do not overwrite'
    assert shutil.disk_usage(native.parent).free > 45 * 2**30
    plan = dict(schema='white-estimated-phase-snr-1000-v1', created_unix=time.time(),
                planned=6000, scenes=list(range(1000)), snrs=SNRS, configuration=str(BINDING),
                frontend_binding=binding, receiver_configuration=config,
                receiver_factory='evaluation.white_phase_frontend_20261106.receiver:Receiver',
                native_directory=str(native), assets=assets, worker_assets=worker_assets,
                runtime=dict(white_plan['runtime']), preflight_position=0,
                automatic_retry=False, training=False,
                dependency_directories=[str(WHITE), str(ABLATION)],
                phase_policy=request['phase_policy'], precision=request['inference_precision'],
                comparisons=request['comparisons'],
                phase_reproduction_absolute_tolerance=1e-12,
                implementation_note='Independent white provenance loader; unchanged frozen phase infer and conditional numerical infer via method resolution order.',
                limitations=['Historical research scenes, not untouched test data.',
                             'Six SNRs share a physical scene.', 'Concurrent time is not an algorithm latency benchmark.'])
    assert plan['runtime']['max_workers'] == 2
    write_json(OUT/'PLAN.json', plan)
    write_json(OUT/'PLAN_HASH.json', dict(sha256=sha256(OUT/'PLAN.json')))
    for name in ('results', 'logs', 'launches'):
        (OUT/name).mkdir(exist_ok=True)
    write_json(OUT/'PREPARED.json', dict(status='PASS', prepared_unix=time.time(), inputs=6000,
        reference_metadata_pairs=6000, assets=len(assets), gpu_preflight_run=False, inference_started=False,
        predecessor_ablation_must_finish_before_any_inference=True,
        verification='Reference summary hashes and inputs checked; actual arrays are re-scored at final report.'))
    return verify()


if __name__ == '__main__':
    prepare()
