"""Small algebra checks for the review, not receiver experiments."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np

root=Path('D:/afdm-gfra')
paper=root/'paper/C-STMP'
out=paper/'checks/notation_formula_review_20261104'
baseline=json.loads((paper/'checks/language_review_20261104/SOURCE_HASHES.json').read_text(encoding='utf-8'))
current={p:hashlib.sha256((root/p).read_bytes()).hexdigest() for p in baseline}
assert current==baseline, 'Manuscript differs from the preserved review baseline'
(out/'SOURCE_HASHES.json').write_text(json.dumps(current,indent=2)+'\n',encoding='utf-8')
rng=np.random.default_rng(20261104)
def complex_array(shape):
    return rng.normal(size=shape)+1j*rng.normal(size=shape)
def rel(a,b):
    return float(np.linalg.norm(a-b)/max(1.,np.linalg.norm(a),np.linalg.norm(b)))
results={}
K,M,N,Q=3,2,4,5
H=complex_array((K,M,N,N)); A=complex_array((Q,K,N)); W=complex_array((Q,M,N))
Y=np.einsum('qkn,kmrn->qmr',A,H)+W
blocks=[h.transpose(2,0,1).reshape(N,M*N) for h in H]
X=np.concatenate(blocks,axis=0); AM=A.reshape(Q,K*N)
YM=Y.reshape(Q,M*N); WM=W.reshape(Q,M*N)
results['mmv_tensor_vs_device_matrix']=rel(YM,AM@X+WM)
results['device_vec_order']=max(rel(h.reshape(-1),b.reshape(-1,order='F')) for h,b in zip(H,blocks))
results['device_block_sum']=rel(YM,sum(A[:,k,:]@blocks[k] for k in range(K))+WM)

gamma=.7; sigma2=.2; n=K*N
xp=complex_array((n,M*N))
C=np.linalg.inv(np.eye(n)/gamma+AM.conj().T@AM/sigma2)
xl=C@(xp/gamma+AM.conj().T@YM/sigma2)
xl2=xp+gamma*AM.conj().T@np.linalg.solve(sigma2*np.eye(Q)+gamma*AM@AM.conj().T,YM-AM@xp)
sv=np.linalg.svd(AM,compute_uv=False)
frac=np.sum(gamma*sv**2/(sigma2+gamma*sv**2))/n
t=np.trace(C).real/n
v=1/(1/t-1/gamma)
results['lmmse_mean_identity']=rel(xl,xl2)
results['svd_trace_identity']=abs(t-gamma*(1-frac))
results['svd_extrinsic_variance']=abs(v-t/frac)
results['svd_extrinsic_mean']=rel(v*(xl/t-xp/gamma),xp+(xl-xp)/frac)

d=6
B=rng.normal(size=(d,d)); T=B@B.T+.3*np.eye(d)
B=rng.normal(size=(d,d)); S=B@B.T+.2*np.eye(d)
J=T@np.linalg.inv(T+S)
post=np.linalg.inv(np.linalg.inv(T)+np.linalg.inv(S))
results['jacobian_right_covariance']=rel(post,J@S)
lam,U=np.linalg.eigh(S); Sh=U@np.diag(np.sqrt(lam))@U.T
# All sign directions remove Monte Carlo error in this small linear example.
signs=np.array([[1. if (i>>j)&1 else -1. for j in range(d)] for i in range(2**d)])
u=rng.normal(size=d); step=.01; total=0.
for z in signs:
    w=Sh@z
    total+=w@(J@(u+step*w)-J@(u-step*w))/(2*step)
results['central_difference_trace_identity']=abs(total/len(signs)-np.trace(J@S))

p=.23; tk=.41; mu=H[0]; U=mu.reshape(M,N*N)
full=p*tk*np.eye(M*N*N)+p*(1-p)*np.outer(mu.reshape(-1),mu.reshape(-1).conj())
average=np.zeros((M,M),dtype=complex)
for i in range(N*N):
    idx=np.arange(M)*(N*N)+i
    average+=full[np.ix_(idx,idx)]/(N*N)
spatial=p*tk*np.eye(M)+p*(1-p)/(N*N)*U@U.conj().T
results['spatial_mixture_covariance']=rel(average,spatial)
results['mixture_average_variance']=abs(np.trace(spatial).real/M-(p*tk+p*(1-p)*np.linalg.norm(mu)**2/(M*N*N)))
cycles=1.7234; beta=2*np.pi*(cycles-np.floor(cycles+.5)); q=np.arange(7)
results['phase_wrap_invariance']=rel(np.exp(1j*q*beta),np.exp(2j*np.pi*q*cycles))
assert max(results.values())<1e-10, results

aux=(paper/'main.aux').read_text(encoding='utf-8')
eqnums=dict(re.findall(r'\\newlabel\{((?:eq:|frontend:eq:)[^}]+)\}\{\{([^}]+)\}',aux))
inventory=[]
for path in [paper/'main.tex',*sorted((paper/'sections').glob('*.tex'))]:
    if path.name=='appendix_second_order_training.tex':
        continue
    src=path.read_text(encoding='utf-8')
    for match in re.finditer(r'\\label\{((?:eq:|frontend:eq:)[^}]+)\}',src):
        label=match.group(1)
        inventory.append({'label':label,'number':eqnums.get(label),'file':str(path.relative_to(root)).replace('\\','/'),
                          'line':src.count('\n',0,match.start())+1})
(out/'EQUATION_INVENTORY.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation={'status':'PROPOSALS_ONLY','manuscript_files_unchanged':len(current),'algebra_checks':results,
            'largest_residual':max(results.values()),'equation_labels_in_current_manuscript':len(inventory),
            'tolerance':1e-10,'scope':'Small synthetic algebra examples; no experiment results, implementation audit, or general correctness proof',
            'manuscript_edits':0,'receiver_experiments':0,'training_runs':0}
(out/'VALIDATION.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(validation,ensure_ascii=True))
