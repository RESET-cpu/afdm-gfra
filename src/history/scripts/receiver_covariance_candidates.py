"""Explicit receiver-only covariance candidates; no truth or file access."""
import numpy as np


def second_moment(x, axis=1):
    z=np.moveaxis(np.asarray(x),axis,0).reshape(x.shape[axis],-1)
    return z@z.conj().T/z.shape[1]


def positive_part(c):
    eig,u=np.linalg.eigh((c+c.conj().T)/2)
    return (u*np.maximum(eig,0))@u.conj().T


def receiver_candidates(query, nominal_variance, observation, operator, noise,
                        activity_prior, initial_power, mean, posterior_covariance, iteration):
    """Inputs are public observations/operators or frozen receiver estimates.

    Spatial second moments are uncentered, consistent with the zero-mean
    working noise model. The exact sample error mean is audited separately.
    Lower-half selection uses observed query energy, never activity labels.
    The residual-plus-covariance identity would be exact in conditional
    expectation for exact posterior moments; here moments are approximate.
    First-linear propagation additionally assumes independent input rows with
    a common spatial covariance. None is asserted to be calibrated in AFDM.
    """
    antennas=query.shape[1];eye=np.eye(antennas)
    raw=second_moment(query)
    selected=np.argsort(np.mean(abs(query)**2,axis=(1,2,3)),kind='stable')[:max(1,len(query)//2)]
    low=second_moment(query[selected])
    cy=second_moment(observation)
    scale=lambda c:c*(antennas*nominal_variance/np.trace(c).real)
    result=dict(nominal_isotropic=nominal_variance*eye,
        query_second_moment=raw,query_shape_nominal_power=scale(raw),
        lower_half_query_second_moment=low,lower_half_shape_nominal_power=scale(low),
        observation_shape_nominal_power=scale(cy),
        posterior_residual_plus_covariance=second_moment(query-mean)+posterior_covariance.mean(axis=0))
    if iteration==1:
        a=operator.reshape(operator.shape[0],-1)
        gamma=activity_prior*initial_power
        gram=a@a.conj().T
        gain=gamma*a.conj().T@np.linalg.inv(noise*np.eye(len(a))+gamma*gram)
        fraction=np.trace(a@gain).real/a.shape[1]
        linear=gain/fraction
        lhl=linear.conj().T@linear
        interference=(np.trace(lhl@gram).real-2*np.trace(a@linear).real+a.shape[1])/a.shape[1]
        thermal=noise*np.trace(lhl).real/a.shape[1]
        signal=positive_part(cy-noise*eye)/(np.linalg.norm(a)**2/len(a))
        result['first_linear_propagation']=interference*signal+thermal*eye
    return result,selected


def compare(estimate, reference):
    estimate=(estimate+estimate.conj().T)/2;reference=(reference+reference.conj().T)/2
    te,tr=np.trace(estimate).real,np.trace(reference).real
    eig,u=np.linalg.eigh(estimate);er,ur=np.linalg.eigh(reference)
    shape=float(np.linalg.norm(estimate/te-reference/tr)/np.linalg.norm(reference/tr))
    recovery=float(np.trace(u[:,-3:].conj().T@reference@u[:,-3:]).real/er[-3:].sum())
    concentration=float(er[-1]/tr)
    ratio=float(te/tr)
    return dict(trace_ratio=ratio,shape_relative_error=shape,
        full_relative_error=float(np.linalg.norm(estimate-reference)/np.linalg.norm(reference)),
        top3_error_energy_recovery=recovery,
        dominant_vector_squared_overlap=float(abs(np.vdot(u[:,-1],ur[:,-1]))**2),
        reference_largest_eigen_fraction=concentration,estimated_largest_eigen_fraction=float(eig[-1]/te),
        estimated_min_eigenvalue=float(eig[0]),
        strong_correlation=concentration>=.15,
        practical_screen_pass=bool(.8<=ratio<=1.25 and shape<=.25 and (concentration<.15 or recovery>=.9)))
