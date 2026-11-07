"""Re-score all three paired methods and report the two planned comparisons."""
import csv
from pathlib import Path
import time
import numpy as np
from .common import (OUT, WHITE, COLORED, METHODS, SNRS, checked, tag, verify,
                     check_phase_record, validate_result)
from utils import read_json, write_json, sha256
from evaluation.storage import arrays
from evaluation.metrics import score_arrays
from evaluation.white_matched_fp32_20261105.report import aggregate, check_metrics


def reference_result(reference, case, method, plan):
    checked(reference['pointer'], reference['pointer_sha256'])
    checked(reference['result'], reference['result_sha256'])
    pointer = read_json(reference['pointer'])
    assert pointer['result'] == reference['result']
    assert pointer['sha256' if method == 'white_known_phase' else 'result_sha256'] == reference['result_sha256']
    path = Path(reference['result']); row = read_json(path)
    assert row['input_files'] == case['files']
    assert (row['scene'], row['index'], row['snr_db']) == (case['scene'], case['index'], case['snr_db'])
    for file, digest in row['files'].items():
        checked(file, digest)
    assert all(str(path.parent/n) in row['files'] for n in ('prediction.npz', 'record.json', 'INPUT_MANIFEST.json'))
    assert read_json(path.parent/'INPUT_MANIFEST.json')['case'] == case
    record, prediction = read_json(path.parent/'record.json'), arrays(path.parent/'prediction.npz')
    assert all(np.isfinite(v).all() for v in prediction.values())
    assert prediction['estimate'].shape == (40, 16, 16, 16)
    np.testing.assert_array_equal(prediction['activity_decision'], prediction['probabilities'] >= .5)
    assert row['iterations'] == record['iterations'] and row['stopping_reason'] == record['stopping_reason']
    if method == 'white_known_phase':
        assert row['status'] == 'COMPLETE' and not row['preflight']
        assert record['configuration'] == plan['receiver_configuration']
        assert record['oracle_phase_supplied'] and not record['receiver_truth_used'] and not record['noise_truth_used']
    else:
        assert row['status'] == 'COMPLETE_SINGLE_CASE'
        old = read_json(COLORED/'PLAN.json')
        check_phase_record(record, prediction, configuration=old['receiver_configuration'],
                           binding=read_json(old['configuration']))
    measured = score_arrays(prediction, arrays(Path(case['ready']).parent/'truth.npz'))
    check_metrics(row['metrics'], measured)
    row.update(metrics=measured, converged=record['converged'])
    return row, prediction


def validate_preflight(plan):
    position = plan['preflight_position']
    row, record, prediction = validate_result(position, plan, preflight=True)
    case = read_json(OUT/'INPUTS.json')[position]
    ref = read_json(OUT/'REFERENCES.json')[position]['colored_estimated_phase']
    _, original = reference_result(ref, case, 'colored_estimated_phase', plan)
    tolerance = plan['phase_reproduction_absolute_tolerance']
    for key in ('phase', 'phase_slopes'):
        np.testing.assert_allclose(prediction[key], original[key], rtol=0, atol=tolerance)
    assert row['peak_working_set_bytes']/2**30 <= plan['runtime']['worker_peak_budget_gib']
    assert row['peak_cuda_reserved_bytes']/2**30 <= plan['runtime']['gpu_budget_gib_per_worker']
    path = OUT/'preflight'/tag(position)/'RESULT.json'
    write_json(OUT/'PREFLIGHT.json', dict(status='PASS', completed_unix=time.time(),
        position=position, result=str(path), result_sha256=sha256(path),
        saved_arrays_rescored=True, estimated_phase_input_verified=True,
        phase_matches_frozen_colored_frontend=True, phase_absolute_tolerance=tolerance,
        unchanged_white_receiver_configuration=True, network_dtype='float32',
        peak_ram_gib=row['peak_working_set_bytes']/2**30,
        peak_cuda_reserved_gib=row['peak_cuda_reserved_bytes']/2**30,
        iterations=record['iterations'], counted_in_main_6000=False))


def summarize():
    plan = verify()
    cases, references = read_json(OUT/'INPUTS.json'), read_json(OUT/'REFERENCES.json')
    assert {p.name for p in (OUT/'results').glob('*.json')} == {tag(i)+'.json' for i in range(6000)}
    rows = {name:[] for name in METHODS}; pairs = []; hashes = {}
    for position, (case, reference) in enumerate(zip(cases, references)):
        folder = Path(case['ready']).parent
        checked(case['ready'], case['ready_sha256'])
        for name, digest in case['files'].items():
            checked(folder/name, digest)
        pointer = OUT/'results'/(tag(position)+'.json'); link = read_json(pointer)
        assert Path(link['result']) == Path(plan['native_directory'])/tag(position)/'RESULT.json'
        checked(link['result'], link['sha256'])
        current, _, prediction = validate_result(position, plan)
        rows['white_estimated_phase'].append(current)
        hashes[str(pointer)] = sha256(pointer)
        hashes[link['result']] = link['sha256']
        hashes.update(current['files'])
        for method in ('colored_estimated_phase', 'white_known_phase'):
            old, old_prediction = reference_result(reference[method], case, method, plan)
            assert old['metrics']['signal_energy'] == current['metrics']['signal_energy']
            if method == 'colored_estimated_phase':
                np.testing.assert_allclose(prediction['phase'], old_prediction['phase'], rtol=0,
                                           atol=plan['phase_reproduction_absolute_tolerance'])
            rows[method].append(old)
            hashes[reference[method]['result']] = reference[method]['result_sha256']
            hashes.update(old['files'])
        for method in METHODS:
            row = rows[method][-1]
            pairs.append(dict(method=method, scene=case['scene'], index=case['index'], snr_db=case['snr_db'],
                full_error=row['metrics']['full_error'], signal_energy=row['metrics']['signal_energy'],
                misses=row['metrics']['misses'], false_alarms=row['metrics']['false_alarms'],
                nmse_db=row['metrics']['nmse_db'], iterations=row['iterations'], converged=row['converged']))
        if (position+1) % 100 == 0:
            write_json(OUT/'VERIFY_PROGRESS.json', dict(checked=position+1, planned=6000, updated_unix=time.time()))
    summary = {method:{str(snr):aggregate([r for r in values if r['snr_db'] == snr]) for snr in SNRS}
               for method, values in rows.items()}
    assert all(v['inputs'] == 1000 and v['decisions'] == 40000 for m in summary.values() for v in m.values())
    differences = {}
    for reference in ('colored_estimated_phase', 'white_known_phase'):
        differences[reference] = {}
        for snr in SNRS:
            new, old = summary['white_estimated_phase'][str(snr)], summary[reference][str(snr)]
            differences[reference][str(snr)] = dict(nmse_db=new['nmse_db']-old['nmse_db'],
                aer=new['aer']-old['aer'], misses=new['misses']-old['misses'],
                false_alarms=new['false_alarms']-old['false_alarms'])
    with (OUT/'PAIRED_CASES.csv').open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(pairs[0])); writer.writeheader(); writer.writerows(pairs)
    write_json(OUT/'SUMMARY.json', dict(status='VERIFIED', methods=summary,
        white_estimated_minus_reference=differences, plan_sha256=sha256(OUT/'PLAN.json'),
        inputs=6000, paired_scenes_per_snr=1000, limitations=plan['limitations']))
    write_json(OUT/'OUTPUT_HASHES.json', hashes)
    verify()
    write_json(OUT/'COMPLETION.json', dict(status='PASS', completed_unix=time.time(), inputs=6000,
        scenes=1000, per_snr=1000, saved_predictions_rescored=18000,
        input_and_output_hashes_verified=True, all_finite_iteration_limit_outputs_retained=True,
        same_estimated_phase_frontend_verified=True, inference_workers_exited=True,
        coordinator_exit_requires_live_followup=True, manuscript_updated=False,
        summary_sha256=sha256(OUT/'SUMMARY.json'), paired_sha256=sha256(OUT/'PAIRED_CASES.csv')))


if __name__ == '__main__':
    summarize()
