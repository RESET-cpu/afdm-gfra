"""One ten-layer pass with nine fixed-message phase parameter updates."""
import time
import numpy as np
import torch
from . import components as base
from .inputs import pack
from .configuration import CONFIG
from .phase_math import observed_covariances
from .phase_update import update


def infer(receiver, inputs, noise, noise_record, beta):
    observation, pilot, rho = inputs.observation, inputs.pilot, inputs.activity_prior
    start=time.perf_counter(); q,k,n=pilot.shape; r=observation.shape[2]
    assert len(receiver.model.layers)==10
    beta=np.array(beta,float);frames=np.repeat(np.arange(q),r)
    y=observation.transpose(0,2,1).reshape(q*r,-1)
    gram=observed_covariances(pilot,np.eye(r*n))
    mean_power=1.0
    def prepare(slopes):
        phi=np.exp(1j*np.arange(q)[:,None]*slopes)
        return receiver.data.prepare_public(dict(y=observation,a=pilot*phi[:,:,None],
            noise=noise,rho=rho),receiver.scale,receiver.device,phase_mode='known',noise_mode='known')[0]
    public=prepare(beta)
    prior=public['y'].new_zeros(public['channel_shape'])
    reference=public['y'].new_tensor(rho*CONFIG['normalized_training_second_moment'])
    variance=reference; steps=[];estimates=[];probs=[]
    counts=np.array([layer.score_evaluations for layer in receiver.model.layers])
    with torch.inference_mode():
        for index,layer in enumerate(receiver.model.layers):
            query,v,_=base.linear_query(public,prior,variance,layer.c_gamma)
            nv=v.expand(len(query))
            conditional=query+torch.exp(layer.c_alpha)*v/2*receiver.model.score_call(layer.score,query,nv)
            probability=torch.sigmoid(layer.activity(query,nv,conditional,rho))
            estimate=probability[:,None,None,None,None]*conditional
            estimates.append(receiver.to_complex(estimate)*receiver.scale)
            probs.append(probability.cpu().numpy().astype(float))
            if index==9:break
            a,yy=public['a'],public['y'];residual=yy-a@pack(estimate)
            count,columns=yy.shape[0]//2,yy.shape[1]
            raw=(residual.square().sum()-count*columns*public['noise'])/(columns*a.square().sum()/2)
            post_v,ratio=base.feedback_variance(raw,v,layer.c_beta,order=receiver.model.variance_calibration_order)
            prior,variance,_=base.damp_gaussian(prior,variance,(estimate-ratio*query)/(1-ratio),post_v/(1-ratio),reference)
            physical=receiver.to_complex(prior)*receiver.scale
            scalar=float(variance)*receiver.scale**2
            assert scalar>0 and np.isfinite(physical).all()
            projection=np.einsum('qkn,kmrn->kqrm',pilot,physical,optimize=True).reshape(k,q*r,-1)
            projection*=np.exp(1j*beta[:,None]*frames)[:,:,None]
            phase_start=time.perf_counter()
            new_beta,rotation,record=update(gram,projection,y,noise,frames,beta,scalar/mean_power)
            # Only the fitted scalar channel rotation is absorbed into the message.
            # This is the same mean used inside the accepted likelihood.
            normalized=receiver.to_complex(prior)*np.exp(1j*rotation)[:,None,None,None]
            prior=torch.as_tensor(np.stack((normalized.real,normalized.imag),axis=1),dtype=prior.dtype,device=prior.device)
            transport_error=float(np.max(abs(receiver.to_complex(prior)-normalized))/max(np.max(abs(normalized)),1e-30))
            assert transport_error<2e-7
            record.update(seconds=time.perf_counter()-phase_start,after_layer=index+1,message_variance=scalar,message_transport_error=transport_error)
            steps.append(record);beta=new_beta;public=prepare(beta)
    if receiver.device=='cuda':torch.cuda.synchronize()
    calls=np.array([layer.score_evaluations for layer in receiver.model.layers])-counts
    np.testing.assert_array_equal(calls,np.ones(10,int))
    receiver.last_layers=estimates
    arrays=dict(estimate=estimates[-1],probabilities=probs[-1],activity_decision=probs[-1]>=.5,
        phase=np.exp(1j*np.arange(q)[:,None]*beta),phase_slopes=beta,noise_variance_estimate=np.asarray(noise))
    record=dict(status='COMPLETE',iterations=10,stopping_reason='FIXED_DEPTH',seconds=time.perf_counter()-start,steps=steps,score_calls_by_layer=calls.tolist(),score_calls=int(calls.sum()),
        checkpoint_sha256=receiver.configuration['checkpoint_sha256'],selected_epoch=receiver.configuration['selected_epoch'],
        noise_record=noise_record,truth_used_in_inference=False,activity_probability_routing=False,
        phase_update_penalty=False,phase_grid_used=False,full_learned_em_claim=False,global_neural_descent_claim=False,
        objective_scope='Isotropic Gaussian message; one exact conditional-moment E-step and generalized M-step between frozen layers')
    return arrays,record
