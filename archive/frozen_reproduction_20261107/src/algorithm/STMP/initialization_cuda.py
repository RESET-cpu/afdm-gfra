"""Double-precision evaluations of the unchanged covariance likelihood.

SciPy retains control of every optimizer and stopping rule. This module only
evaluates the original objective/derivatives; captured operations avoid Python
kernel-launch overhead. No training or approximate covariance is introduced.
"""
import time
import numpy as np
import torch


class CudaInitialization:
    def __init__(self, gram, y, noise, frames, rho, device):
        self.device=device
        self.k,self.d,_=gram.shape
        self.rho=float(rho);self.span=float(max(frames.max(),1))
        self.noise=float(noise);self.m=y.shape[1]
        self.gram=torch.as_tensor(gram,dtype=torch.complex128,device=device).contiguous()
        self.y=torch.as_tensor(y,dtype=torch.complex128,device=device).contiguous()
        # Preserve the original sample-covariance construction for the scalar objective.
        self.sample=torch.as_tensor(y@y.conj().T/self.m,dtype=torch.complex128,device=device)
        self.eye=torch.eye(self.d,dtype=torch.complex128,device=device)
        self.frames=torch.as_tensor(frames,dtype=torch.float64,device=device)
        self.lag=1j*(self.frames[:,None]-self.frames[None,:])
        self.factor_cov=self.noise*self.eye.clone()
        self.local_base=self.noise*self.eye.clone()
        self.local_gram=self.gram[0].clone()
        self.local_x=torch.tensor([1.,0.],dtype=torch.float64,device=device)
        self.joint_x=torch.zeros(2*self.k,dtype=torch.float64,device=device)
        self._base_source=None
        self.calls=dict(factor=0,local=0,joint=0)
        self.graphs={};self.outputs={}
        started=time.perf_counter()
        with torch.inference_mode():
            for name,function in [('factor',self._factor_forward),('value',self._value_forward),
                                  ('local',self._local_forward),('joint',self._joint_forward)]:
                stream=torch.cuda.Stream(device=device)
                stream.wait_stream(torch.cuda.current_stream(device))
                with torch.cuda.stream(stream):
                    for _ in range(3):self.outputs[name]=function()
                torch.cuda.current_stream(device).wait_stream(stream)
                graph=torch.cuda.CUDAGraph()
                with torch.cuda.graph(graph,stream=stream):self.outputs[name]=function()
                self.graphs[name]=graph
            torch.cuda.synchronize(device)
        self.setup_seconds=time.perf_counter()-started

    def _factor(self,covariance,weight_required=True):
        factor,info=torch.linalg.cholesky_ex(covariance,upper=False,check_errors=False)
        inverse=torch.cholesky_solve(self.eye,factor,upper=False)
        value=2*torch.log(torch.diagonal(factor).real).sum()+(inverse*self.sample.T).sum().real
        if not weight_required:return value,inverse,None,info
        transformed=inverse@self.y
        weight=inverse-(transformed@transformed.mH)/self.m
        return value,inverse,(weight+weight.mH)/2,info

    def _factor_forward(self):
        value,inverse,weight,info=self._factor(self.factor_cov)
        return torch.stack((value,info.to(torch.float64))),inverse,weight

    def _value_forward(self):
        value,inverse,_,info=self._factor(self.factor_cov,False)
        return torch.stack((value,info.to(torch.float64))),inverse

    def _local_forward(self):
        gamma=self.local_x[0]*self.rho;beta=self.local_x[1]/self.span
        phi=torch.exp(1j*self.frames*beta)
        rotated=self.local_gram*phi[:,None]*phi[None,:].conj()
        value,_,weight,info=self._factor(self.local_base+gamma*rotated)
        power_gradient=self.rho*(weight.T*rotated).sum().real
        phase_gradient=gamma/self.span*(weight.T*(self.lag*rotated)).sum().real
        return torch.stack((value,power_gradient,phase_gradient,info.to(torch.float64)))

    def _joint_forward(self):
        power=self.joint_x[:self.k]*self.rho;beta=self.joint_x[self.k:]/self.span
        phi=torch.exp(1j*beta[:,None]*self.frames)
        rotated=self.gram*phi[:,:,None]*phi[:,None,:].conj()
        covariance=self.noise*self.eye+(power[:,None,None]*rotated).sum(dim=0)
        value,_,weight,info=self._factor(covariance)
        power_gradient=self.rho*(weight.T[None,:,:]*rotated).sum(dim=(1,2)).real
        phase_gradient=power/self.span*(weight.T[None,:,:]*(self.lag*rotated)).sum(dim=(1,2)).real
        return torch.cat((value.reshape(1),power_gradient,phase_gradient,info.to(torch.float64).reshape(1)))

    def _copy(self,destination,array):
        destination.copy_(torch.as_tensor(np.asarray(array)))

    @staticmethod
    def _check(packed):
        if packed[-1]!=0 or not np.isfinite(packed).all():
            raise FloatingPointError('CUDA covariance factorization or likelihood evaluation failed')

    def factor(self,covariance,weight_required=True):
        self.calls['factor']+=1
        name='factor' if weight_required else 'value'
        with torch.inference_mode():
            self._copy(self.factor_cov,covariance);self.graphs[name].replay()
            output=self.outputs[name];packed=output[0].cpu().numpy()
            self._check(packed)
            inverse=output[1].cpu().numpy()
            weight=output[2].cpu().numpy() if weight_required else None
        return float(packed[0]),inverse,weight

    def local(self,x,gram,base):
        self.calls['local']+=1
        with torch.inference_mode():
            if self._base_source is not base:
                self._copy(self.local_base,base);self._copy(self.local_gram,gram)
                self._base_source=base
            self._copy(self.local_x,x);self.graphs['local'].replay()
            packed=self.outputs['local'].cpu().numpy()
        self._check(packed)
        return float(packed[0]),packed[1:-1].copy()

    def joint(self,x):
        self.calls['joint']+=1
        with torch.inference_mode():
            self._copy(self.joint_x,x);self.graphs['joint'].replay()
            packed=self.outputs['joint'].cpu().numpy()
        self._check(packed)
        return float(packed[0]),packed[1:-1].copy()
