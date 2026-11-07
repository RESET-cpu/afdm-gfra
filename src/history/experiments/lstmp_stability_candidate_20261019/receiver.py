"""Damp a proposed estimate when a declared quadratic objective increases.

Adaptive damping is motivated by Vila et al., arXiv:1412.2005, Section II.
This particular quadratic objective and probability interpolation are project
choices, not that paper's Bethe cost or a reproduction of its GAMP algorithm.
The scalar quadratic minimizer follows direct expansion along the segment.
No statement of channel-NMSE monotonicity or exact posterior calibration follows.
"""
import torch
from experiments.lstmp_candidate_20261019 import receiver as base
from experiments.lstmp_candidate_20261019.common import CONFIG
from experiments.lstmp_candidate_20261019.data import pack


def damp_proposal(public, previous, old_probability, proposal, logits, prior_power):
    """Use only Y, A, noise, prior second moment, and current/previous predictions.

    J(X)=||A X-Y||^2 + lambda ||X||^2, lambda=noise/prior_power.
    Along X+t*d, J(t)-J(0)=2*t*slope+t^2*curvature. Keep the
    full proposed update if it decreases J. Otherwise use the minimizer on [0,1].
    Probability interpolation represents a convex mixture of the two approximate
    beliefs; the residual variance remains a separate iteration parameter.
    """
    y,a=public['y'],public['a']
    penalty=public['noise']/prior_power
    residual=a@pack(previous)-y
    difference=proposal-previous
    projected=a@pack(difference)
    # Scalar accumulation in float64 protects the acceptance comparison. Matrix
    # operations and networks retain the current float32 execution settings.
    inner=lambda u,v:(u.double()*v.double()).sum()
    slope=inner(residual,projected)+penalty*inner(previous,difference)
    curvature=inner(projected,projected)+penalty*inner(difference,difference)
    full_change=2*slope+curvature
    minimizer=(-slope/curvature.clamp_min(torch.finfo(torch.float64).tiny)).clamp(0.,1.)
    coefficient=torch.where(full_change<=0,torch.ones_like(minimizer),minimizer).to(y.dtype)
    # Keep the full accepted proposal bit-for-bit, instead of cancelling previous
    # in previous+(proposal-previous). Both branches preserve autograd.
    estimate=torch.where(coefficient==1,proposal,previous+coefficient*difference)
    mixed=old_probability+coefficient*(torch.sigmoid(logits)-old_probability)
    probability_floor=torch.finfo(logits.dtype).eps
    mixed_logits=torch.logit(mixed.clamp(probability_floor,1-probability_floor))
    final_logits=torch.where(coefficient==1,logits,mixed_logits)
    old_cost=inner(residual,residual)+penalty*inner(previous,previous)
    new_residual=a@pack(estimate)-y
    new_cost=inner(new_residual,new_residual)+penalty*inner(estimate,estimate)
    details=dict(damping=float(coefficient.detach()),quadratic_cost_before=float(old_cost.detach()),
        quadratic_cost_after=float(new_cost.detach()),proposal_quadratic_cost=float((old_cost+full_change).detach()),
        quadratic_relative_increase=float(((new_cost-old_cost)/old_cost.clamp_min(1e-30)).detach()))
    return estimate,final_logits,details


class Receiver(base.Receiver):
    def forward(self,public,*,return_messages=False):
        y,a,rho=public['y'],public['a'],public['rho']
        prior=y.new_zeros(public['channel_shape'])
        prior_power=rho*CONFIG.get('normalized_training_second_moment',1.)
        variance=y.new_tensor(prior_power)
        previous=prior
        old_probability=y.new_full((len(prior),),rho)
        outputs,diagnostics,messages=[],[],[]
        for layer in self.layers:
            c=layer.calibration
            r,v,analytical_v=base.linear_query(public,prior,variance,c[0])
            nv=v.expand(len(r))
            score=self.score_call(layer.score,r,nv)
            conditional=r+torch.exp(c[1])*v/2*score
            logits=layer.activity(r,nv,conditional,rho)
            proposal=torch.sigmoid(logits)[:,None,None,None,None]*conditional
            estimate,logits,details=damp_proposal(public,previous,old_probability,proposal,logits,prior_power)
            previous,old_probability=estimate,torch.sigmoid(logits)
            residual=y-a@pack(estimate)
            frames,columns=y.shape[0]//2,y.shape[1]
            raw=(residual.square().sum()-frames*columns*public['noise'])/(columns*a.square().sum()/2)
            post_v,feedback_ratio=base.feedback_variance(raw,v,c[2],order=self.variance_calibration_order)
            prior=(estimate-feedback_ratio*r)/(1-feedback_ratio)
            variance=post_v/(1-feedback_ratio)
            outputs.append((estimate,logits))
            diagnostics.append(dict(query_variance=float(v.detach()),raw_residual_variance=float(raw.detach()),
                feedback_variance=float(post_v.detach()),negative_raw_variance=bool(raw.detach()<0),
                feedback_ratio=float(feedback_ratio.detach()),next_variance=float(variance.detach()),
                partial_feedback_mean_gain=float(1/(1-feedback_ratio.detach())),
                linear_variance=float(analytical_v.detach()),score_log_scale=float(c[1].detach()),
                feedback_log_scale=float(c[2].detach()),
                out_of_pretraining_support=not(CONFIG['complex_variance_support'][0]<=float(v.detach())<=CONFIG['complex_variance_support'][1]),
                ratio_near_ceiling=bool(feedback_ratio.detach()>.99*CONFIG['receiver']['maximum_feedback_variance_ratio']),**details))
            if return_messages:messages.append(dict(query=r.detach(),conditional=conditional.detach(),next_prior=prior.detach()))
        return (outputs,diagnostics,messages) if return_messages else (outputs,diagnostics)
