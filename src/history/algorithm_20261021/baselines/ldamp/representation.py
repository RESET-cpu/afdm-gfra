"""Fixed unitary representation of the complete effective AFDM channel.

Undo the two DAFT axes, reindex the time matrix by cyclic lag, then take a
unitary DFT along time. This is an invertible coordinate representation, not an
estimate of physical delays, Dopplers, or path counts. Full-delay CPP effects
and fractional-delay leakage remain in all coefficients.
"""
import numpy as np
from afdm_jadcedd.system import config
from afdm_jadcedd.system.afdm.path_operator_multicycle_full import daft_matrix


def beam_transform(value,inverse=False):
    """Fixed unitary DFT on the known 4x4 UPA, antenna axis 1.

    No estimated or true direction enters this transform. The same transform
    applies to observations (Q,M,R) and channel/query blocks (K,M,R,N).
    """
    value=np.asarray(value)
    if value.shape[1]!=16:raise ValueError('The declared 4x4 array is required')
    shaped=value.reshape(value.shape[0],4,4,*value.shape[2:])
    function=np.fft.ifft2 if inverse else np.fft.fft2
    return function(shaped,axes=(1,2),norm='ortho').reshape(value.shape)


class Representation:
    def __init__(self,size=16):
        self.size=size
        self.a=daft_matrix(size,config.C1,config.C2)
        coordinate=np.arange(size)
        self.chirp1=np.exp(-2j*np.pi*config.C1*coordinate**2)
        self.chirp2=np.exp(-2j*np.pi*config.C2*coordinate**2)
        self.time=np.arange(size)[:,None]
        self.index=(self.time-np.arange(size)[None,:])%size

    def forward(self,channel):
        h=np.asarray(channel)
        if h.shape[-2:]!=(self.size,self.size):raise ValueError('Unexpected AFDM dimensions')
        # A = diag(chirp2) F diag(chirp1). Applying these exact factors avoids
        # dense 16x16 contractions on every Monte Carlo denoiser evaluation.
        value=self.chirp2.conj()[:,None]*h*self.chirp2[None,:]
        value=np.fft.fft(np.fft.ifft(value,axis=-2,norm='ortho'),axis=-1,norm='ortho')
        time=self.chirp1.conj()[:,None]*value*self.chirp1[None,:]
        lag=time[...,self.time,self.index]
        return np.fft.fft(lag,axis=-2,norm='ortho')

    def inverse(self,coefficients):
        lag=np.fft.ifft(coefficients,axis=-2,norm='ortho')
        time=lag[...,self.time,self.index]
        value=self.chirp1[:,None]*time*self.chirp1.conj()[None,:]
        value=np.fft.ifft(np.fft.fft(value,axis=-2,norm='ortho'),axis=-1,norm='ortho')
        return self.chirp2[:,None]*value*self.chirp2.conj()[None,:]

    def pack_transform(self,value):
        channels=value.shape[1]//2
        complex_value=value[:,:channels].numpy()+1j*value[:,channels:].numpy()
        transformed=self.forward(complex_value)
        return np.concatenate([transformed.real,transformed.imag],axis=1).astype(np.float32)
