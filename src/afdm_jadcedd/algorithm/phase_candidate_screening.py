"""Vectorized physical alias screening; same candidate set and score."""
import numpy as np
from afdm_jadcedd.algorithm.phase_candidate_atoms import geometry
from afdm_jadcedd.algorithm.unknown_phase_model import FRAME_DURATION_S
from afdm_jadcedd.system import config as cfg


def atoms_at_positions(pilot,user,positions):
    n=cfg.N
    r,s,transform=geometry(n,cfg.C1,cfg.C2)
    delay=positions[:,0,None,None]
    frequency=positions[:,1,None,None]
    eta=r-delay
    wrapped=np.remainder(eta,n)
    rho=np.floor(2*cfg.C1*wrapped+s/n)
    phase=(cfg.C2*s**2+cfg.C1*(eta**2-delay**2)+s*wrapped/n-rho*wrapped+frequency*r/n)
    basis=np.exp(2j*np.pi*phase)/np.sqrt(n)
    h=np.einsum('ri,gis->grs',transform,basis,optimize=False)
    raw=np.einsum('qn,grn->gqr',pilot[:,user],h,optimize=False)
    derivative=2*np.pi*cfg.DELTA_F_HZ*FRAME_DURATION_S*np.arange(len(pilot))[:,None]
    return (raw*np.exp(1j*derivative*frequency)).reshape(len(positions),-1)


def physical_candidates(pilot,user,received,peaks,controls,old_position=None):
    positions=[]
    for delay,beta,_ in peaks:
        cycles=np.arange(-int(np.ceil(cfg.NU_MAX_HZ*FRAME_DURATION_S))-1,
                         int(np.ceil(cfg.NU_MAX_HZ*FRAME_DURATION_S))+2)
        values=(beta/(2*np.pi)+cycles)/FRAME_DURATION_S/cfg.DELTA_F_HZ
        positions.extend((delay,f) for f in values[abs(values)<=cfg.NU_MAX_HZ/cfg.DELTA_F_HZ])
    positions=np.asarray(positions)
    atoms=atoms_at_positions(pilot,user,positions)
    correlation=np.einsum('gl,lm->gm',atoms.conj(),received,optimize=False)
    norms=np.sum(abs(atoms)**2,axis=1)
    scores=np.sum(abs(correlation)**2,axis=1)/norms
    order=np.argsort(-scores,kind='stable')[:controls.alias_refinements]
    selected=[positions[i] for i in order]
    if old_position is not None:selected.append(np.asarray(old_position).copy())
    return selected
