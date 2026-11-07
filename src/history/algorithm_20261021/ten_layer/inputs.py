"""Public observation conversion; no training banks or labels are loaded."""
import numpy as np
import torch

def pack(x):
    users, components, antennas, samples, inputs = x.shape
    if components != 2:
        raise ValueError('Expected real/imaginary channel components')
    return x.permute(1, 0, 4, 2, 3).reshape(2*users*inputs, antennas*samples)


def unpack(x, shape):
    users, components, antennas, samples, inputs = shape
    if components != 2 or x.shape != (2*users*inputs, antennas*samples):
        raise ValueError('Packed channel and requested dimensions disagree')
    return x.reshape(2, users, inputs, antennas, samples).permute(1, 0, 3, 4, 2)


def block(a, device):
    return torch.tensor(np.block([[a.real, -a.imag], [a.imag, a.real]]), dtype=torch.float32, device=device)


def prepare_public(values, scale, device, *, phase_mode, noise_mode):
    """Select public fields before frontend work. Truth arrays are never read here."""
    from afdm_jadcedd.algorithm.baselines.noise_estimation import estimate_spatial_noise
    from afdm_jadcedd.algorithm.unknown_phase_model import UnknownPhaseInput
    from afdm_jadcedd.system.observation import ReceiverInput,array_sha256
    from afdm_jadcedd.algorithm import phase_estimation_optimized as phase
    y, rho = np.asarray(values['y']),float(values['rho'])
    record = dict(phase_mode=phase_mode,noise_mode=noise_mode,truth_used_in_inference=False)
    if noise_mode=='estimated':
        noise,record['noise_estimation']=estimate_spatial_noise(y)
    elif noise_mode=='known':
        noise=float(values['noise'])
    else:
        raise ValueError('noise_mode must be known or estimated')
    if phase_mode=='estimated':
        inputs=UnknownPhaseInput(y,np.asarray(values['pilot']),noise,rho)
        fitted,record['phase_estimation']=phase.estimate(inputs,phase.Controls())
        operator=inputs.at_estimated_phase(fitted['phase_slopes']).operator
    elif phase_mode=='known':
        operator=np.asarray(values['a'])
    else:
        raise ValueError('phase_mode must be known or estimated')
    record['oracle_phase_supplied']=phase_mode=='known'
    record['oracle_noise_supplied']=noise_mode=='known'
    record['used_noise_variance']=noise
    record['observation_sha256']=array_sha256(y)
    record['operator_sha256']=array_sha256(operator)
    frames,users,inputs=operator.shape
    if y.shape[0]!=frames or y.shape[1:]!=(16,16) or inputs!=16:
        raise ValueError('K and Q may vary; the score channel block must remain 16 x 16 x 16')
    if not np.isfinite(scale) or scale<=0 or not np.isfinite(noise) or noise<=0:
        raise ValueError('Positive scale and noise variance required')
    a=operator.reshape(frames,users*inputs)
    u,s,vh=np.linalg.svd(a,full_matrices=False)
    normalized=y.reshape(frames,-1)/scale
    public=dict(a=block(a,device),uh=block(u.conj().T,device),vv=block(vh.conj().T,device),
        s=torch.tensor(s,dtype=torch.float32,device=device),
        y=torch.tensor(np.concatenate((normalized.real,normalized.imag)),dtype=torch.float32,device=device),
        noise=noise/scale**2,rho=rho,channel_shape=(users,2,*y.shape[1:],inputs),
        physical_input=ReceiverInput(y,operator,noise,rho))
    return public,record
