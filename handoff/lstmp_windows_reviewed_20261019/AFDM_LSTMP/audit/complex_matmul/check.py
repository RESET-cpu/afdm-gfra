"""Check observed complex-matmul warnings against independent contractions."""
from pathlib import Path
import inspect,json,os,sys,warnings
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
os.environ['AFDM_LSTMP_ROOT']=str(ROOT)
sys.path.insert(0,str(ROOT/'runs/lstmp_fresh_20261019/source_experiment'))
import common
from afdm_jadcedd.system.afdm import continuous
from afdm_jadcedd.algorithm.proposed import gaussian
from threadpoolctl import threadpool_limits
threadpool_limits(1)
contraction=lambda a,b:np.einsum('ik,kj->ij',a,b,optimize=False)
namespace=dict(continuous.__dict__,contraction=contraction)
source=inspect.getsource(continuous.continuous_path_matrix).replace(
    'daft_matrix(n, c1, c2) @ (doppler * delayed)',
    'contraction(daft_matrix(n,c1,c2),doppler*delayed)')
exec(source,namespace)
reference_path=namespace['continuous_path_matrix']
namespace=dict(gaussian.__dict__,contraction=contraction)
source=inspect.getsource(gaussian.gaussian_extrinsic).replace(
    '((root @ basis) * used) @ basis.conj().T @ root',
    'contraction(contraction(contraction(root,basis)*used,basis.conj().T),root)')
exec(source,namespace)
reference_extrinsic=namespace['gaussian_extrinsic']
rng=np.random.default_rng(2026101988)
errors=[]
with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter('always')
    for delay in (0.,.2,17.8,123.4):
        args=(16,delay,3000.,1e-6,37.,1/32,np.sqrt(2)/16)
        actual=continuous.continuous_path_matrix(*args)
        reference=reference_path(*args)
        assert np.isfinite(actual).all()
        errors.append(float(np.linalg.norm(actual-reference)/np.linalg.norm(reference)))
    q=rng.normal(size=(16,16))+1j*rng.normal(size=(16,16))
    cavity=contraction(q,q.conj().T)+np.eye(16)
    posterior=.3*cavity
    mean=rng.normal(size=(2,16,3,4))+1j*rng.normal(size=(2,16,3,4))
    residual=.7*mean
    actual=gaussian.gaussian_extrinsic(mean,posterior,residual,cavity)
    reference=reference_extrinsic(mean,posterior,residual,cavity)
    for a,b in zip(actual,reference):
        assert np.isfinite(a).all()
        errors.append(float(np.linalg.norm(a-b)/max(np.linalg.norm(b),1e-20)))
assert max(errors)<3e-12
report=dict(status='PASS',scope='Independent contraction comparison for two observed warning locations; no source changes or training',
            max_relative_error=max(errors),tolerance=3e-12,numpy_version=np.__version__,
            warnings_observed=[dict(file=Path(w.filename).name,line=w.lineno,message=str(w.message)) for w in captured],
            interpretation='Outputs finite and match independent contractions in these checks; warning cause not asserted')
(Path(__file__).parent/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
