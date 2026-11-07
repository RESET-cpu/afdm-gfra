"""Damp Gaussian feedback in natural parameters, preserving network outputs.

The variance-dependent coefficient is a project heuristic, not a theorem or
an equation claimed from L-STMP. It must pass independent development checks.
"""
import torch
from . import receiver_base as base
from experiments.lstmp_candidate_20261019.common import CONFIG
from experiments.lstmp_candidate_20261019.data import pack


def damp_gaussian(previous_mean,previous_variance,proposed_mean,proposed_variance,reference_variance):
    """Geometric interpolation of two Gaussian messages with positive variance."""
    amount=(reference_variance/proposed_variance).clamp(max=1.)
    variance=1/((1-amount)/previous_variance+amount/proposed_variance)
    mean=variance*((1-amount)*previous_mean/previous_variance+amount*proposed_mean/proposed_variance)
    # Preserve the accepted original message exactly, including rounding.
    return (torch.where(amount==1,proposed_mean,mean),
            torch.where(amount==1,proposed_variance,variance),amount)


class Receiver(base.Receiver):
    def forward(self,public,*,return_messages=False):
        y,a,rho=public['y'],public['a'],public['rho']
        prior=y.new_zeros(public['channel_shape'])
        reference=y.new_tensor(rho*CONFIG.get('normalized_training_second_moment',1.))
        variance=reference
        outputs,diagnostics,messages=[],[],[]
        for layer in self.layers:
            c=layer.calibration
            r,v,analytical_v=base.linear_query(public,prior,variance,c[0])
            nv=v.expand(len(r))
            conditional=r+torch.exp(c[1])*v/2*self.score_call(layer.score,r,nv)
            logits=layer.activity(r,nv,conditional,rho)
            estimate=torch.sigmoid(logits)[:,None,None,None,None]*conditional
            residual=y-a@pack(estimate)
            frames,columns=y.shape[0]//2,y.shape[1]
            raw=(residual.square().sum()-frames*columns*public['noise'])/(columns*a.square().sum()/2)
            post_v,ratio=base.feedback_variance(raw,v,c[2],order=self.variance_calibration_order)
            proposed_mean=(estimate-ratio*r)/(1-ratio)
            proposed_variance=post_v/(1-ratio)
            prior,variance,amount=damp_gaussian(prior,variance,proposed_mean,proposed_variance,reference)
            outputs.append((estimate,logits))
            diagnostics.append(dict(query_variance=float(v.detach()),raw_residual_variance=float(raw.detach()),
                feedback_variance=float(post_v.detach()),feedback_ratio=float(ratio.detach()),
                proposed_variance=float(proposed_variance.detach()),next_variance=float(variance.detach()),
                damping=float(amount.detach()),linear_variance=float(analytical_v.detach()),
                out_of_pretraining_support=not(CONFIG['complex_variance_support'][0]<=float(v.detach())<=CONFIG['complex_variance_support'][1])))
            if return_messages:messages.append(dict(query=r.detach(),conditional=conditional.detach(),next_prior=prior.detach()))
        return (outputs,diagnostics,messages) if return_messages else (outputs,diagnostics)
