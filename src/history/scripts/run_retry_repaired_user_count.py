"""Formal paired user-count runner for the independently verified retry rule."""
import argparse
from pathlib import Path
import repair_stability_retry as r
from stability_damping_retry import RetryReceiver
import run_repaired_user_count as native_runner

OUT=Path('D:/afdm-gfra-cpu/results_proposed_stability_retry_20261019')
native_runner.OUT=OUT
native_runner.TARGET=OUT/'user_count'
# The original supervisor must dispatch this entry point, including its binding.
native_runner.__file__=str(Path(__file__).resolve())
native_runner.paired.EstimatedNoiseProposedReceiver=RetryReceiver
RetryReceiver.audit_root=OUT/'retained_attempts'


def prepare():
    regression=r.d.paired.read(r.OUT/'regression_previous_failure/SUMMARY.json')
    if not regression['passed'] or not regression['known_failure_first_attempt_exact']:
        raise ValueError('The frozen rule did not pass the separate known-failure regression check')
    native_runner.prepare()
    path=native_runner.TARGET/'PLAN.json'
    plan=r.d.paired.read(path)
    freeze=r.d.paired.read(r.OUT/'FROZEN_CANDIDATE.json')
    plan['execution'].update(freeze['execution'])
    plan['execution'].update(all_attempt_costs_counted=True,failed_attempt_predictions_retained=True)
    for source in (Path(__file__),r.d.ROOT/'scripts/run_repaired_user_count.py'):
        plan['source_and_weight_sha256'][str(source.resolve())]=r.d.paired.sha(source)
    regression_path=r.OUT/'regression_previous_failure/SUMMARY.json'
    plan['source_and_weight_sha256'][str(regression_path.resolve())]=r.d.paired.sha(regression_path)
    plan['known_failure_regression']='Passed separately; not counted among the 60 independent acceptance cases'
    r.d.paired.save(path,plan)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','run','worker'])
    parser.add_argument('--worker',type=int)
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='worker':native_runner.worker(args.worker)
    else:native_runner.supervise()
