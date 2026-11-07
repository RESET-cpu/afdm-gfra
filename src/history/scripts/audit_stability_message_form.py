"""Read-only message algebra audit on the existing development input bank."""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
from pathlib import Path
import numpy as np
import evaluate_saved_baseline_inputs as p
from afdm_jadcedd.algorithm.proposed.linear import SpatialLinear


def main():
    root = p.ROOT/'runs/stability_repair_20261019'
    target = p.ROOT/'results/stability_message_form_20261019/AUDIT.json'
    if target.exists():
        raise ValueError('Preserve previous audit')
    config = p.read(p.MODEL)
    rows = []
    rng = np.random.default_rng(202610194000001)
    for folder in sorted((root/'bank/development').iterdir()):
        identity = p.read(folder/'READY.json')
        for name, digest in identity['sha256'].items():
            assert p.sha(folder/name) == digest
        data = p.arrays(folder/'input.npz')
        y = data['observation']/config['scale']
        noise = float(data['noise_variance'])/config['scale']**2
        linear = SpatialLinear(data['operator'], y.shape[1], noise)
        a = linear.a
        c = .1
        mean = (rng.standard_normal((linear.users, linear.antennas, y.shape[2], linear.columns))
                + 1j*rng.standard_normal((linear.users, linear.antennas, y.shape[2], linear.columns)))*.01
        post, post_cov, query, query_cov = linear.update(y, mean, np.eye(linear.antennas)*c)
        gain = c*a.conj().T @ np.linalg.inv(noise*np.eye(a.shape[0])+c*a@a.conj().T)
        fraction = np.trace(gain@a).real/a.shape[1]
        packed = linear.pack(mean)
        residual = y.reshape(a.shape[0], -1)-a@packed
        expected_post = linear.unpack(packed+gain@residual)
        expected_query = linear.unpack(packed+gain@residual/fraction)
        relative = lambda x,z: float(np.linalg.norm(x-z)/max(np.linalg.norm(z),1e-15))
        own, thermal, condition = [], [], []
        for k in range(linear.users):
            sl = slice(k*linear.columns, (k+1)*linear.columns)
            w = gain[sl]/fraction
            block = a[:, sl]
            own.append(float(np.linalg.norm(w@block-np.eye(linear.columns))/np.sqrt(linear.columns)))
            covariance = w@w.conj().T
            isotropic = np.eye(linear.columns)*np.trace(covariance).real/linear.columns
            thermal.append(relative(covariance, isotropic))
            condition.append(float(np.linalg.cond(block)))
        rows.append(dict(case=folder.name, input_manifest_sha256=p.sha(folder/'READY.json'),
            posterior_relative_error=relative(post, expected_post), query_relative_error=relative(query, expected_query),
            posterior_covariance_relative_error=relative(post_cov, np.eye(linear.antennas)*c*(1-fraction)),
            query_covariance_relative_error=relative(query_cov, np.eye(linear.antennas)*c*(1-fraction)/fraction),
            own_response_deviation_min=float(min(own)), own_response_deviation_max=float(max(own)),
            thermal_covariance_isotropy_deviation_min=float(min(thermal)),
            thermal_covariance_isotropy_deviation_max=float(max(thermal)),
            user_block_condition_median=float(np.median(condition)), user_block_condition_max=float(max(condition))))
    traces = []
    for method in ['damping0.2', 'damping0.2_fp32', 'damping0.1_budget1200_fp32']:
        for users in [20,60,100]:
            source = root/'evaluations/development'/method/f'scene000_users{users}'/'record.json'
            if not source.exists():
                continue
            record = p.read(source)
            trace = record['trace']
            traces.append(dict(method=method, users=users, source_sha256=p.sha(source),
                iterations=record['iterations'], stopping_reason=record['stopping_reason'],
                clipped_feedback_iterations=sum(t['projected_eigenvalues']>0 for t in trace),
                unsupported_iterations=sum(t['unsupported_users']>0 for t in trace),
                rejected_site_iterations=sum(t['rejected_site_users']>0 for t in trace),
                largest_raw_variance_fraction=max(t['variance_fraction_max'] for t in trace),
                first_query_all_activity_probabilities_one=all(x==1 for x in trace[0]['probabilities_per_user'])) )
    passed = all(max(r[k] for k in ['posterior_relative_error','query_relative_error',
        'posterior_covariance_relative_error','query_covariance_relative_error'])<1e-10 for r in rows)
    p.save(target,dict(algebra_passed=passed, cases=len(rows), rows=rows, saved_trace_audit=traces,
        truth_used=False, interpretation='Gaussian algebra checks only. Synthetic incoming means and declared positive noise are used; no claim about statistical calibration or receiver accuracy.',
        damping_audit=dict(author_commit='0c75680c966dcb8e46250de146f4c27e9294c283',
            author_url='https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L103-L118',
            conclusion='Both author implementation and current implementation retain previously damped messages in both directions. Paper equations 57-58 notation alone should not be interpreted as an implementation bug.'),
        source_sha256={str(Path(__file__)):p.sha(Path(__file__)),
            str(p.ROOT/'src/afdm_jadcedd/algorithm/proposed/linear.py'):p.sha(p.ROOT/'src/afdm_jadcedd/algorithm/proposed/linear.py')}))
    print(dict(algebra_passed=passed,cases=len(rows),saved_trace_audit=traces),flush=True)


if __name__ == '__main__':
    main()
