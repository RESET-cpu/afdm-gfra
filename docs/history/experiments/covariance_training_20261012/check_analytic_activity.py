"""Offline feasibility check for Cai (26)--(30) with antenna covariances.

The formula is a Gaussian approximation to activity evidence, not a recovery
of the unknown normalizing constant from local moments. No receiver, training
stage, or frozen experiment recipe is changed by this script.
"""
from pathlib import Path
import argparse
import json
import shutil
import sys
import warnings

import numpy as np
from threadpoolctl import threadpool_limits

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from train import digest, dump


def gaussian_activity_log_ratio(r, mean, covariance, risk):
    """Matrix extension of Cai (26)--(30); complex CN covariance convention.

For Z=C^-1/2 R, G=C^-1/2 F, S=C^-1/2 B C^-1/2, the
normalized Gaussian extrinsic message gives
ell=L*logdet(I-S)+||Z||_F^2-tr((Z-G)^H (I-S)^-1 (Z-G)).
The prior log odds are not included. No eigenvalue clipping is performed.
"""
    values, vectors = np.linalg.eigh(covariance)
    if values.min() <= 0:
        raise ValueError("Positive C required")
    invroot = np.einsum('mi,i,ni->mn', vectors, values**-.5, vectors.conj(), optimize=False)
    z = np.einsum('mn,nl->ml', invroot, r, optimize=False)
    g = np.einsum('mn,nl->ml', invroot, mean, optimize=False)
    s = np.einsum('ij,jk,kl->il', invroot, risk, invroot, optimize=False)
    s = (s+s.conj().T)/2
    spectrum = np.linalg.eigvalsh(s)
    if spectrum.min() <= 0 or spectrum.max() >= 1:
        raise ValueError("This proper Gaussian extrinsic construction requires 0 < S < I")
    gap = np.eye(len(s))-s
    delta = z-g
    logdet = np.log(np.linalg.eigvalsh(gap)).sum()
    return float(r.shape[1]*logdet + np.sum(abs(z)**2)
                 - np.vdot(delta, np.linalg.solve(gap, delta)).real)


def algebra_checks():
    rng = np.random.default_rng(202610120983)
    def cn(shape):
        return (rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    def covariance(m):
        a = cn((m,m))
        return np.einsum('mi,ni->mn',a,a.conj(),optimize=False)/m+.3*np.eye(m)
    errors = []
    product_errors = []
    numerical_warnings = []
    # Noncommuting C and T, nonzero means, and complex multicolumn data.
    for m, columns in ((1,1),(3,7),(16,256)):
        for _ in range(10):
            c, t = covariance(m), covariance(m)
            r, u = cn((m,columns)), cn((m,columns))
            ci, ti = np.linalg.inv(c), np.linalg.inv(t)
            b = np.linalg.inv(ci+ti)
            ci_r = np.einsum('mi,il->ml',ci,r,optimize=False)
            ti_u = np.einsum('mi,il->ml',ti,u,optimize=False)
            mean = np.einsum('mi,il->ml',b,ci_r+ti_u,optimize=False)
            # Independently check the native complex matmul despite known
            # local BLAS floating-point warnings; never accept NaN equality.
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                native_mean = b@(ci@r+ti@u)
            numerical_warnings.extend(str(item.message) for item in caught)
            assert np.isfinite(native_mean).all() and np.isfinite(mean).all()
            np.testing.assert_allclose(native_mean,mean,rtol=2e-11,atol=2e-11,equal_nan=False)
            product_errors.append(float(np.max(abs(native_mean-mean))))
            actual = gaussian_activity_log_ratio(r, mean, c, b)
            expected = (columns*(np.linalg.slogdet(c)[1]-np.linalg.slogdet(c+t)[1])
                        +np.vdot(r,ci_r).real-np.vdot(r-u,np.linalg.solve(c+t,r-u)).real)
            assert np.isfinite(actual) and np.isfinite(expected)
            np.testing.assert_allclose(actual,expected,rtol=2e-11,atol=2e-9,equal_nan=False)
            errors.append(abs(actual-expected))
    try:
        gaussian_activity_log_ratio(np.ones((2,1)),np.zeros((2,1)),np.eye(2),1.2*np.eye(2))
    except ValueError:
        pass
    else:
        raise AssertionError("Non-normalizable Gaussian extrinsic accepted")
    return dict(gaussian_exact_reference_cases=len(errors), maximum_absolute_log_ratio_error=max(errors),
                noncommuting_complex_covariances_checked=True,invalid_extrinsic_rejected=True,
                eigenvalue_clipping_applied=False,all_outputs_explicitly_finite=True,
                native_matmul_warnings=numerical_warnings,
                native_matmul_vs_independent_contraction_max_absolute_difference=max(product_errors))


def run(run_dir, output):
    run_dir, output = Path(run_dir).resolve(), Path(output).resolve()
    complete = json.loads((run_dir/'complete.json').read_text())
    selected = run_dir/f"validation_epoch{complete['selected_epoch']:03d}.npz"
    weight = run_dir/'second_best.pt'
    if complete['status']!='COMPLETED' or complete['weight_sha256']!=digest(weight):
        raise ValueError("Completed selected second checkpoint required")
    first = json.loads((run_dir.parent/'FIRST.json').read_text())
    if complete['first_sha256'] != first['weight_sha256']:
        raise ValueError("Frozen first identity differs")
    with np.load(selected,allow_pickle=False) as arrays, np.load(run_dir/'validation_parameters.npz',allow_pickle=False) as params:
        s = arrays['prediction'][:,0].astype(float)+1j*arrays['prediction'][:,1].astype(float)
        spectrum = np.linalg.eigvalsh((s+s.conj().swapaxes(-1,-2))/2)
        masks = dict(all=np.ones(len(s),bool),white=params['beta']==0,colored=params['beta']>0)
        masks.update({f'variance_1e{k}_to_1e{k+1}':(params['variance']>=10.**k)&(params['variance']<10.**(k+1)) for k in range(-3,2)})
        groups = {}
        for name,mask in masks.items():
            current = spectrum[mask]
            groups[name] = dict(samples=len(current), upper_bound_violations=int((current[:,-1]>=1).sum()),
                upper_bound_violations_with_1e_minus6_margin=int((current[:,-1]>=1+1e-6).sum()),
                fraction_upper_bound_violations=float(np.mean(current[:,-1]>=1)),
                negative_beyond_1e_minus6=int((current[:,0]<-1e-6).sum()),
                max_eigenvalue_quantiles=np.quantile(current[:,-1],[0,.5,.9,.99,1]).tolist())
    checks = algebra_checks()
    output.mkdir(parents=True,exist_ok=False)
    result = dict(status='COMPLETED',scope='Offline algebra and saved active-conditional synthetic validation outputs only; not AER or actual iterative queries',
        first_epoch=first['epoch'],second_epoch=complete['selected_epoch'],groups=groups,algebra=checks,
        caveats=['B is the fixed-first conditional error second moment, not necessarily the exact posterior covariance.',
                 'B<C is not a pointwise theorem for general priors; its failure does not alone prove a network error.',
                 'Tiny float32 negative eigenvalues are reported separately from violations above one.',
                 'A valid Gaussian extrinsic message does not establish accurate evidence for the physical non-Gaussian prior.',
                 'Antennas retain full covariance but cross-column correlations and pseudo-covariance are omitted.'],
        sources=dict(paper='https://arxiv.org/html/2506.00581v2#S3.SS2',equations='(24)-(30)',
            author_code='https://github.com/chang-cai/score-massive-connectivity/blob/0c75680c966dcb8e46250de146f4c27e9294c283/main_stmp_jadce.py#L193-L210',
            author_code_scope='The inspected commit uses zero-mean fixed-power Gaussian activity evidence rather than the learned extrinsic channel parameters.'),
        identities={str(path.relative_to(ROOT)):digest(path) for path in (Path(__file__),weight,selected,run_dir/'complete.json',run_dir/'validation_parameters.npz')})
    dump(output/'RESULTS.json',result)
    shutil.copyfile(__file__,output/Path(__file__).name)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--second-run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with threadpool_limits(limits=1):
        result=run(args.second_run,args.output)
    print(json.dumps(dict(groups=result['groups'],algebra=result['algebra']),indent=2))
