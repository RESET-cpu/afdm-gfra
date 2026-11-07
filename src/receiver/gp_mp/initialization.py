"""Physical phase initialization with Gaussian marginal likelihood.

One physical atom per user; independent complex antenna gains with learned
nonnegative powers. This is a working covariance model, not the true spatial
channel prior. Same physical search budgets as the existing initializer.
Tipping & Faul (2003), author version Section 2.1 (7)-(8); complex multi-column
coordinate formulas are derived in the candidate README, not quoted as theirs.
"""
from dataclasses import asdict
import time
import numpy as np
from scipy.linalg import cho_factor
from scipy.linalg import cho_solve
from scipy.optimize import minimize
from channel import config as cfg
from channel.phase import wrap
from channel.atoms import sampling_grid
from channel.atoms import delay_bounds
from channel.atoms import ORDER
from channel.unknown_phase import UnknownPhaseInput
from channel.unknown_phase import FRAME_DURATION_S
from channel.phase_atoms import sensed_atom
from receiver.frontend.phase_screening import atoms_at_positions
from receiver.frontend.phase_estimation import Controls
from receiver.frontend.phase_estimation import coarse_scores
from receiver.frontend.phase_estimation import candidates


def inverse_covariance(design,powers,noise):
    if noise<=0 or np.any(powers<0):raise ValueError('Positive noise and nonnegative powers required')
    b=design*np.sqrt(powers)[None,:]
    f=cho_factor(np.eye(b.shape[1])+b.conj().T@b/noise,lower=True,check_finite=True)
    inverse=np.eye(len(b))/noise-b@cho_solve(f,b.conj().T)/noise**2
    inverse=(inverse+inverse.conj().T)/2
    logdet=len(b)*np.log(noise)+2*np.log(np.diag(f[0]).real).sum()
    return inverse,float(logdet)


def coordinate_value(power,s,t,columns):
    return float(np.log1p(power*s)-power*t/(columns*(1+power*s)))


def optimum_power(s,t,columns):
    if s<=0 or t<0:raise ValueError('Positive precision energy and nonnegative correlation required')
    return max(0.,(t/(columns*s)-1)/s)


def statistics(atom,inverse,solved):
    s=float(np.vdot(atom,inverse@atom).real)
    projection=atom.conj()@solved
    return s,float(np.vdot(projection,projection).real)


def objective(position,pilot,user,inverse,solved):
    atom,derivatives,_=sensed_atom(pilot,user,position,derivatives=True)
    weighted=inverse@atom;projection=atom.conj()@solved
    s=float(np.vdot(atom,weighted).real);t=float(np.vdot(projection,projection).real)
    ds=2*np.real(derivatives.conj()@weighted)
    dt=2*np.real((derivatives.conj()@solved)@projection.conj())
    # Maximizing t/s also minimizes the marginal contribution after profiling power.
    return -t/(s*solved.shape[1]),-(dt-t/s*ds)/(s*solved.shape[1])


def refine(pilot,user,inverse,solved,position,controls):
    lo,hi=delay_bounds(position[0])
    frequency_step=1/(controls.phase_bins*cfg.DELTA_F_HZ*FRAME_DURATION_S)
    limit=cfg.NU_MAX_HZ/cfg.DELTA_F_HZ
    bounds=[(lo,hi),(max(-limit,position[1]-2*frequency_step),min(limit,position[1]+2*frequency_step))]
    scale=np.array([1/ORDER,frequency_step]);center=np.asarray(position,float)
    def evaluate(z):
        value,gradient=objective(center+scale*z,pilot,user,inverse,solved)
        return value,gradient*scale
    scaled=[((a-center[j])/scale[j],(b-center[j])/scale[j]) for j,(a,b) in enumerate(bounds)]
    fit=minimize(evaluate,np.zeros(2),jac=True,bounds=scaled,method='L-BFGS-B',
        options=dict(maxiter=controls.refinement_iterations,ftol=1e-12,gtol=1e-8))
    position=center+scale*fit.x
    return position,sensed_atom(pilot,user,position),dict(success=bool(fit.success),status=int(fit.status),
        iterations=int(fit.nit),message=str(fit.message))


def alias_starts(pilot,user,peaks,inverse,solved,controls,old_position):
    positions=[]
    for delay,beta,_ in peaks:
        cycles=np.arange(-int(np.ceil(cfg.NU_MAX_HZ*FRAME_DURATION_S))-1,int(np.ceil(cfg.NU_MAX_HZ*FRAME_DURATION_S))+2)
        values=(beta/(2*np.pi)+cycles)/FRAME_DURATION_S/cfg.DELTA_F_HZ
        positions.extend((delay,f) for f in values[abs(values)<=cfg.NU_MAX_HZ/cfg.DELTA_F_HZ])
    positions=np.asarray(positions);atoms=atoms_at_positions(pilot,user,positions)
    s=np.einsum('gl,gl->g',atoms.conj(),(inverse@atoms.T).T).real
    t=np.sum(abs(atoms.conj()@solved)**2,axis=1)
    order=np.argsort(-t/s,kind='stable')[:controls.alias_refinements]
    starts=[positions[i] for i in order]
    if old_position is not None:starts.append(old_position.copy())
    return starts


def estimate(inputs,controls=Controls(),observer=None):
    if not isinstance(inputs,UnknownPhaseInput):raise TypeError('Only public unknown-phase input accepted')
    if controls.local_second_sweep:raise ValueError('This candidate uses the retained full search budget')
    tick=time.perf_counter();pilot=inputs.pilot;noise=inputs.noise_variance
    y3=inputs.observation.transpose(0,2,1);y=y3.reshape(-1,y3.shape[-1]);m=y.shape[1]
    atoms,coordinates,_=sampling_grid(controls.screening_doppler_step)
    raw=np.einsum('qkn,grn->kgqr',pilot,atoms,optimize=False)
    k=pilot.shape[1]
    priorities=[float(coarse_scores(raw[u],y3,controls.phase_bins,controls.batched_correlations).max()) for u in range(k)]
    order=np.argsort(-np.asarray(priorities),kind='stable')
    design=np.zeros((len(y),k),complex);powers=np.zeros(k);positions=np.zeros((k,2))
    current=float(len(y)*np.log(noise)+np.linalg.norm(y)**2/(noise*m));initial_value=current
    trace=[];updates=[]
    for sweep in range(controls.sweeps):
        before=current
        for user in order:
            without=powers.copy();without[user]=0.
            inverse,logdet=inverse_covariance(design,without,noise);solved=inverse@y
            base_value=float(logdet+np.vdot(y,solved).real/m)
            old_atom=design[:,user].copy();old_power=float(powers[user])
            options=[(current,old_power,positions[user].copy(),old_atom,'unchanged')]
            if np.any(old_atom):
                s,t=statistics(old_atom,inverse,solved);power=optimum_power(s,t,m)
                options.append((base_value+coordinate_value(power,s,t,m),power,positions[user].copy(),old_atom,'current_position_profiled_power'))
            # Coarse correlations propose locations; exact whitened evidence ranks aliases and refinements.
            peaks=candidates(raw[user],(noise*solved).reshape(y3.shape),coordinates,controls)
            starts=alias_starts(pilot,int(user),peaks,inverse,solved,controls,positions[user] if sweep else None)
            statuses=[]
            for start in starts:
                position,atom,status=refine(pilot,int(user),inverse,solved,start,controls)
                s,t=statistics(atom,inverse,solved);power=optimum_power(s,t,m)
                options.append((base_value+coordinate_value(power,s,t,m),power,position,atom,'refined_position'))
                statuses.append(status)
            value,power,position,atom,label=min(options,key=lambda row:row[0])
            if value>current+1e-9*max(1.,abs(current)):raise FloatingPointError('Marginal coordinate objective increased')
            updates.append(dict(sweep=sweep+1,user=int(user),before=current,after=value,power_before=old_power,power_after=power,
                chosen=label,attempted_candidates=len(starts),candidate_status=statuses))
            current=float(value);powers[user]=power;positions[user]=position;design[:,user]=atom
        inverse,logdet=inverse_covariance(design,powers,noise)
        actual=float(logdet+np.vdot(y,inverse@y).real/m)
        if not np.isclose(actual,current,rtol=1e-8,atol=1e-8):raise FloatingPointError('Rank-one and full marginal objectives disagree')
        if actual>before+1e-8*max(1.,abs(before)):raise FloatingPointError('Marginal sweep objective increased')
        current=actual
        row=dict(sweep=sweep+1,marginal_objective=actual,previous_marginal_objective=before,positive_powers=int(np.sum(powers>0)),seconds=time.perf_counter()-tick)
        trace.append(row)
        if observer is not None:observer(row)
    gains=powers[:,None]*(design.conj().T@(inverse@y))
    prediction=design@gains;doppler=positions[:,1]*cfg.DELTA_F_HZ
    slopes=wrap(2*np.pi*doppler*FRAME_DURATION_S)
    arrays=dict(phase_slopes=slopes,doppler_hz=doppler,folded_delay_samples=positions[:,0],path_gains=gains,
        path_powers=powers,fitted_observation=prediction.reshape(y3.shape).transpose(0,2,1))
    record=dict(status='COMPLETE',seconds=time.perf_counter()-tick,controls=asdict(controls),
        method='Physical atom Gaussian marginal likelihood with per-user nonnegative gain variance',
        truth_used_in_inference=False,known_activity_used=False,input_fields=list(inputs.arguments()),
        spatial_gain_prior='Independent antenna columns, common user variance; working approximation only',
        phase_model='one physical Doppler per candidate user',channel_approximation='one dominant physical path per user during initialization',
        initial_marginal_objective=initial_value,trace=trace,refinements=updates,
        fitted_powers=powers.tolist(),fitted_positions=positions.tolist(),
        final_residual_to_public_noise_energy=float(np.linalg.norm(y-prediction)**2/(y.size*noise)),
        hard_activity_decision_passed_to_receiver=False,phase_search_during_receiver_iterations=False)
    return arrays,record
