"""Finite-memory Anderson acceleration, Walker--Ni (2011), Algorithm AA.

The ridge term and rejection bounds below are explicit candidate safeguards,
not a convergence theorem for this receiver. Only public iteration states enter.
"""
import numpy as np


class Anderson:
    def __init__(self,memory=5,ridge=1e-8):
        self.memory=memory;self.ridge=ridge;self.history=[]

    def clear(self):
        self.history.clear()

    def step(self,x,g):
        f=g-x
        self.history.append((f.copy(),g.copy()))
        self.history=self.history[-self.memory:]
        n=len(self.history)
        info=dict(anderson_used=False,anderson_history=n,anderson_coefficient_l1=1.)
        if n<2:return g,info
        gram=np.asarray([[np.vdot(a[0],b[0]).real for b in self.history] for a in self.history])
        scale=max(float(np.trace(gram)/n),1e-30)
        try:
            alpha=np.linalg.solve(gram/scale+self.ridge*np.eye(n),np.ones(n))
            alpha=alpha/alpha.sum()
        except np.linalg.LinAlgError:
            self.clear();return g,info
        magnitude=float(np.sum(abs(alpha)));info['anderson_coefficient_l1']=magnitude
        if not np.isfinite(alpha).all() or magnitude>100:
            self.clear();return g,info
        mixed=sum(weight*item[1] for weight,item in zip(alpha,self.history))
        if not np.isfinite(mixed).all() or np.linalg.norm(mixed-x)>100*max(np.linalg.norm(f),1e-12):
            self.clear();return g,info
        info['anderson_used']=True
        return mixed,info


def pack(r,v,out,out_v):
    scale=np.sqrt(r.size)
    return np.concatenate((r.ravel(),out.ravel(),[scale*np.log(np.trace(v).real/len(v)),
        scale*np.log(np.trace(out_v).real/len(out_v))]))


def unpack(vector,shape):
    size=int(np.prod(shape));scale=np.sqrt(size)
    logs=vector[-2:].real/scale
    if not np.isfinite(logs).all() or np.any(abs(logs)>25):
        raise ValueError('Rejected accelerated variance')
    v,p=np.exp(logs)
    return vector[:size].reshape(shape),np.eye(shape[1])*v,vector[size:2*size].reshape(shape),np.eye(shape[1])*p


def residual(x,g,shape,damping):
    size=int(np.prod(shape));scale=np.sqrt(size)
    ratios=[np.linalg.norm(g[a:b]-x[a:b])/max(np.linalg.norm(x[a:b]),np.linalg.norm(g[a:b]),1e-12)
        for a,b in ((0,size),(size,2*size))]
    ratios.extend(abs((g[-2:]-x[-2:])/scale))
    return float(max(ratios)/damping)
