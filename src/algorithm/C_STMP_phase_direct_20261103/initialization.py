"""Direct wrapped-slope initialization from a training covariance marginal.

This is a Gaussian marginal-likelihood approximation, not a path model. Output
rows and antennas are treated as replicate columns only in this initializer;
their true dependence is not asserted to vanish. No delay or physical Doppler
parameter is estimated. The entire training covariance is never matched to an
online example; only its fixed column marginal is retained.
"""
import time
import numpy as np
from project import ROOT
from utils import sha256
from algorithm.STMP.fast_initialization import _Sample, coordinate, joint


def column_moment(moment, rows, columns):
    moment=np.asarray(moment,complex)
    if moment.shape != (rows*columns, rows*columns):
        raise ValueError('Training moment and channel dimensions differ')
    result=np.einsum('rnrp->np',moment.reshape(rows,columns,rows,columns))/rows
    return (result+result.conj().T)/2


def estimate(inputs, policy, receiver_configuration):
    started=time.perf_counter()
    if policy['method'] != 'column_covariance':
        raise ValueError('Unknown initialization method')
    path=ROOT/policy['training_second_moment']
    if sha256(path) != policy['training_second_moment_sha256']:
        raise ValueError('Frozen training moment changed')
    q,k,n=inputs.pilot.shape
    scale=receiver_configuration['scale']
    with np.load(path,allow_pickle=False) as saved:
        moment=column_moment(saved['second_moment'],inputs.observation.shape[2],n)/scale**2
    gram=np.einsum('qkn,nt,skt->kqs',inputs.pilot,moment,inputs.pilot.conj(),optimize=True)
    gram=(gram+gram.conj().transpose(0,2,1))/2
    sample=_Sample(inputs.observation.reshape(q,-1)/scale)
    noise=inputs.noise_variance/scale**2
    frames=np.arange(q)
    beta,power,coordinates=coordinate(gram,sample,noise,frames,inputs.activity_prior,
        sweeps=policy['sweeps'],local_maxiter=policy['local_iterations'])
    beta,power,optimization=joint(gram,sample,noise,frames,beta,power,inputs.activity_prior,
        maxiter=policy['joint_iterations'])
    return beta,dict(method='column_covariance_marginal_likelihood',seconds=time.perf_counter()-started,
        physical_path_search_used=False,phase_grid_used=False,training_moment_sha256=policy['training_second_moment_sha256'],
        covariance_order=q,training_column_moment_shape=list(moment.shape),
        initial_covariance='noise only; slope enters via marginal power directional derivative',
        coordinates=coordinates,optimization=optimization,fitted_powers=power.tolist(),
        limitation='Column-covariance Gaussian approximation; dependent channel rows are treated as replicates.')
