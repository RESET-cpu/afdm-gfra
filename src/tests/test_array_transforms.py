"""Fourier basis and real-coordinate covariance preservation."""
import numpy as np
import torch
from networks.array_transforms import spatial_fft,spatial_matrix,packed_transform


def test_transform_against_explicit_kronecker_dft():
    n=4;indices=np.arange(n);d=np.exp(-2j*np.pi*indices[:,None]*indices[None,:]/n)/np.sqrt(n)
    expected=np.kron(np.fft.fftshift(d,axes=0),np.fft.fftshift(d,axes=0))
    f=spatial_matrix();np.testing.assert_allclose(f,expected,rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(f.conj().T@f,np.eye(16),rtol=1e-12,atol=1e-12)
    rng=np.random.default_rng(35);x=rng.normal(size=(2,16,5,3))+1j*rng.normal(size=(2,16,5,3))
    actual=spatial_fft(x);np.testing.assert_allclose(actual,np.einsum('ij,bjrn->birn',expected,x),rtol=1e-12,atol=1e-12)
    np.testing.assert_allclose(spatial_fft(actual,inverse=True),x,rtol=1e-12,atol=1e-12)
    packed=torch.tensor(np.stack([x.real,x.imag],axis=1))
    a,b=torch.tensor(f.real),torch.tensor(f.imag)
    y=packed_transform(packed,a,b)
    np.testing.assert_allclose(y[:,0].numpy()+1j*y[:,1].numpy(),actual,rtol=1e-12,atol=1e-12)
    torch.testing.assert_close(packed_transform(y,a,b,inverse=True),packed,rtol=1e-12,atol=1e-12)
    # Deterministic white covariance preservation; no Monte Carlo tolerance.
    q=np.block([[f.real,-f.imag],[f.imag,f.real]])
    np.testing.assert_allclose(q@q.T,np.eye(32),rtol=1e-12,atol=1e-12)


