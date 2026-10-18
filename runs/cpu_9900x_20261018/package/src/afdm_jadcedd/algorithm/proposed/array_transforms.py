"""Unitary UPA transform, m=z+Nz*y; centered beam coordinates, full support."""
import numpy as np
import torch


def spatial_fft(channels, rows=4, columns=4, *, inverse=False):
    """Complex [..., M, R, N]; only the two UPA axes are transformed."""
    x=np.asarray(channels)
    if x.shape[-3] != rows*columns: raise ValueError('UPA shape mismatch')
    grid=x.reshape(*x.shape[:-3],rows,columns,*x.shape[-2:])
    axes=(-4,-3)
    if inverse:
        result=np.fft.ifft2(np.fft.ifftshift(grid,axes=axes),axes=axes,norm='ortho')
    else:
        result=np.fft.fftshift(np.fft.fft2(grid,axes=axes,norm='ortho'),axes=axes)
    return result.reshape(x.shape).astype(x.dtype,copy=False)


def spatial_matrix(rows=4, columns=4):
    """F in beam=F@antenna, independently constructed from a basis bank."""
    m=rows*columns
    basis=np.eye(m,dtype=np.complex128).reshape(m,m,1,1)
    return spatial_fft(basis,rows,columns).reshape(m,m).T.copy()


def packed_transform(x, real, imag, *, inverse=False):
    """Real [B,2,M,R,N] operation supported on MPS without complex tensors."""
    if x.ndim!=5 or x.shape[1]!=2 or x.shape[2]!=real.shape[0]:
        raise ValueError('packed complex channel shape mismatch')
    a,b=x[:,0].flatten(2),x[:,1].flatten(2)
    if inverse: real,imag=real.T,-imag.T
    out_a=torch.matmul(real,a)-torch.matmul(imag,b)
    out_b=torch.matmul(imag,a)+torch.matmul(real,b)
    return torch.stack((out_a,out_b),dim=1).reshape_as(x)
