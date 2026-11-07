"""Network-free, analytic operator controls; not an AFDM receiver benchmark.

Use existing independent development operators only. No truth or weights loaded.
For a synthetic iid Gaussian input with variance c, compute exact first-query
error covariance and its cross-covariance with the input. Preserve all outputs.
"""
import os
for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cai_operator_applicability_20261019'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def statistics(values):
    return dict(min=float(np.min(values)), median=float(np.median(values)),
                max=float(np.max(values)))


def inspect(a, users, width, c, noise):
    rows, dim = a.shape
    gram = a @ a.conj().T
    power = np.trace(gram).real / rows
    u, s, vh = np.linalg.svd(a, full_matrices=False)
    gain = c * s / (noise + c * s*s)
    fraction = np.sum(s * gain) / dim
    w = (vh.conj().T * (gain / fraction)) @ u.conj().T
    v = c * (1 - fraction) / fraction
    total = c * gram + noise * np.eye(rows)
    own, shape, calibration, variance, minimum = [], [], [], [], []
    for k in range(users):
        sl = slice(k*width, (k+1)*width)
        wk, ak = w[sl], a[:, sl]
        response = wk @ ak
        cov = c*np.eye(width) + wk@total@wk.conj().T - c*(response+response.conj().T)
        cov = (cov + cov.conj().T)/2
        mean = np.trace(cov).real/width
        own.append(np.linalg.norm(response-np.eye(width))/np.sqrt(width))
        shape.append(np.linalg.norm(cov-mean*np.eye(width))/(mean*np.sqrt(width)))
        calibration.append(mean/v)
        variance.append(mean)
        minimum.append(np.linalg.eigvalsh(cov).min())
    trace_error = abs(np.mean(variance)/v-1)
    assert trace_error < 1e-10, trace_error
    assert min(minimum) > -1e-10*v
    return dict(rows=rows, columns=dim, sensing_ratio=rows/dim,
                row_orthogonality_relative=float(np.linalg.norm(gram-power*np.eye(rows))/(power*np.sqrt(rows))),
                nonzero_singular_condition=float(s.max()/s.min()),
                own_response_deviation=statistics(own),
                within_user_error_covariance_anisotropy=statistics(shape),
                per_user_mse_over_declared_variance=statistics(calibration),
                global_trace_relative_error=float(trace_error),
                declared_query_variance=float(v))


def main():
    OUT.mkdir(exist_ok=False)
    config_path = ROOT/'runs/proposed_auxiliary_100_cuda_graph_20261019/n50000/receiver.json'
    config = json.loads(config_path.read_text())
    protected = {str(config_path.relative_to(ROOT)): sha(config_path)}
    for key in ('first_checkpoint','second_checkpoint','evidence_checkpoint'):
        path = ROOT/config[key]
        assert sha(path) == config[key+'_sha256']
        protected[str(path.relative_to(ROOT))] = sha(path)
    for name in ('linear.py', 'denoiser.py', 'iterations.py', 'moments.py'):
        path = ROOT/'src/afdm_jadcedd/algorithm/proposed'/name
        protected[str(path.relative_to(ROOT))] = sha(path)
    protocol = dict(seed=202610197000001, physical_scenes=4, users=[20,40,60,80,100],
                    scope='Analytic first-query geometry with synthetic iid Gaussian input; no receiver inference or training.',
                    truth_used=False, gamma='Native initialization rho times normalized training second moment',
                    controls=['actual','same_row_space_flat_spectrum','same_spectrum_random_right_vectors','cai_style_T1_same_ratio'],
                    limitations=['Controls change the observation model and are not physical AFDM pilot proposals.',
                                 'Cai-style T=1 has equal scalar sensing ratio, not the original paper operating point.',
                                 'Gaussian input is a synthetic analytical control, not a model asserted for physical channels.',
                                 'Per-user covariance is over the 16 mixed channel coordinates; it is not antenna covariance.',
                                 'No feedback, activity sparsity or learned denoiser is present; cannot establish closed-loop performance.',
                                 'Four physical scenes, twenty conditions, not twenty independent scenes.'])
    (OUT/'PROTOCOL.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    rng = np.random.default_rng(protocol['seed'])
    results = []
    for folder in sorted((ROOT/'runs/stability_repair_20261019/bank/development').iterdir()):
        ready = json.loads((folder/'READY.json').read_text())
        path = folder/'input.npz'
        assert sha(path) == ready['sha256']['input.npz']
        protected[str(path.relative_to(ROOT))] = sha(path)
        with np.load(path) as data:
            operator = data['operator']
            noise = float(data['noise_variance'])/config['scale']**2
            c = float(data['activity_prior'])*config['initialization']['normalized_training_second_moment']
        rows, users, width = operator.shape
        a = operator.reshape(rows,-1)
        u,s,vh = np.linalg.svd(a,full_matrices=False)
        power = float(np.mean(s*s))
        z = rng.standard_normal((a.shape[1],rows))+1j*rng.standard_normal((a.shape[1],rows))
        q,_ = np.linalg.qr(z,mode='reduced')
        assert rows == width
        selected = rng.choice(users,width,replace=False)
        cai = np.zeros_like(a)
        for n in range(width):
            cai[n,n::width] = np.sqrt(power/users)*np.exp(-2j*np.pi*selected[n]*np.arange(users)/users)
        controls = dict(actual=a,
                        same_row_space_flat_spectrum=np.sqrt(power)*(u@vh),
                        same_spectrum_random_right_vectors=(u*s)@q.conj().T,
                        cai_style_T1_same_ratio=cai)
        assert np.allclose(controls['same_spectrum_random_right_vectors']@controls['same_spectrum_random_right_vectors'].conj().T,a@a.conj().T,rtol=1e-10,atol=1e-10*power)
        result = dict(case=folder.name,seed=ready['seed'],users=users,
                      controls={name:inspect(matrix,users,width,c,noise) for name,matrix in controls.items()})
        assert result['controls']['cai_style_T1_same_ratio']['own_response_deviation']['max'] < 1e-10
        results.append(result)
    for relative,digest in protected.items():
        assert sha(ROOT/relative) == digest, relative
    report = dict(protocol=protocol,status='COMPLETE',cases=results,
                  protected_files_unchanged=True,protected_sha256=protected,
                  script_sha256=sha(Path(__file__)), training_started=False,formal_experiments='PAUSED')
    (OUT/'REPORT.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    for name in protocol['controls']:
        print(name, json.dumps({metric:statistics([case['controls'][name][metric]['median'] for case in results])
                               for metric in ('own_response_deviation','within_user_error_covariance_anisotropy','per_user_mse_over_declared_variance')}))
    print('Maximum global trace error:',max(c['global_trace_relative_error'] for row in results for c in row['controls'].values()))


if __name__ == '__main__':
    main()
