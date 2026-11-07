"""Experimental AFDM adaptation of learned score-based turbo message passing.

Wei & Yuan, arXiv:2610.17785v1, III-B--D, equations (5)--(13).
Differences: general AFDM operator, real-coordinate score factor 1/2,
unknown user activity, and explicitly constrained variance updates.
The pretrained AFDM RefineNet is used, not the paper's NCSN++ backbone.
"""
from copy import deepcopy
import math
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint


def pack(channel):
    k,m,r,n=channel.shape
    return channel.permute(0,3,1,2).reshape(k*n,m*r)


def unpack(matrix, shape):
    k,m,r,n=shape
    return matrix.reshape(k,n,m,r).permute(0,2,3,1)


def linear_posterior(y, operator, mean, variance, noise):
    """Exact scalar-prior LMMSE for arbitrary A, no row-orthogonal shortcut."""
    a=operator.reshape(operator.shape[0],-1)
    x=pack(mean); observation=y.reshape(len(a),-1)
    gram=a@a.mH
    system=variance*gram+noise*torch.eye(len(a),dtype=a.dtype,device=a.device)
    chol=torch.linalg.cholesky(system)
    correction=variance*a.mH@torch.cholesky_solve(observation-a@x,chol)
    response=variance*torch.trace(torch.cholesky_solve(gram,chol)).real/a.shape[1]
    return unpack(x+correction,mean.shape),variance*(1-response)


def extrinsic(post_mean, post_variance, prior_mean, prior_variance):
    variance=post_variance*prior_variance/(prior_variance-post_variance)
    mean=(prior_variance*post_mean-post_variance*prior_mean)/(prior_variance-post_variance)
    return mean,variance


def evidence_forward(network, query, variance, conditional_mean):
    """Same pretrained evidence features, with gradients through the score mean.

    Original EvidenceNetwork.inputs deliberately detaches that mean for its
    separate training stage. End-to-end training must not use that detach.
    """
    x=query.reshape(len(query),-1,query.shape[-2],query.shape[-1])
    f=conditional_mean.reshape_as(x)
    factor=torch.sqrt(2/(1+variance))[:,None,None,None]
    maps=torch.cat((factor*x,factor*f),dim=1)
    energy=lambda value:2*value.square().flatten(1).mean(1)/variance
    rf=2*(x*f).flatten(1).mean(1)/variance
    scalar=torch.stack((torch.log(variance)/5,torch.log1p(energy(x)),
                        torch.log1p(energy(f)),torch.sign(rf)*torch.log1p(abs(rf)),
                        torch.log1p(energy(x-f))),dim=1)
    condition=network.condition(scalar[:,:1])
    for block,bias in zip(network.blocks,network.biases):
        maps=block(maps)+bias(condition)[:,:,None,None]
    return network.readout(torch.cat((maps.flatten(1),scalar),dim=1))[:,0]


class Layer(nn.Module):
    def __init__(self, score, activity, microbatch=8):
        super().__init__()
        self.score=score;self.activity=activity;self.microbatch=microbatch
        self.gamma_raw=nn.Parameter(torch.zeros((),dtype=torch.float64))
        self.alpha_raw=nn.Parameter(torch.zeros((),dtype=torch.float64))
        self.beta_raw=nn.Parameter(torch.tensor(math.log(.01),dtype=torch.float64))

    def nonlinear(self, query, variance):
        means=[];logits=[]
        alpha=torch.exp(math.log(2)*torch.tanh(self.alpha_raw))
        for block in query.split(self.microbatch):
            packed=torch.stack((block.real,block.imag),dim=1).float()
            label=variance.expand(len(block)).float()
            def evaluate(x,v,alpha,network=self.score,evidence=self.activity):
                # DirectCaiNetwork's tensor-only path avoids a device sync per chunk.
                score=network.network(x.reshape(len(x),-1,x.shape[-2],x.shape[-1]),v).reshape_as(x)
                conditional=x+(alpha.float()*v/2)[:,None,None,None,None]*score
                ell=evidence_forward(evidence,x,v,conditional)
                return conditional,ell
            if self.training:
                conditional,ell=checkpoint(evaluate,packed,label,alpha,use_reentrant=False)
            else:
                conditional,ell=evaluate(packed,label,alpha)
            means.append(torch.complex(conditional[:,0],conditional[:,1]).to(query.dtype))
            logits.append(ell.double())
        return torch.cat(means),torch.cat(logits),alpha

    def forward(self,y,operator,mean,variance,noise,activity_prior):
        post,analytic=linear_posterior(y,operator,mean,variance,noise)
        analytic_fraction=(analytic/variance).clamp(1e-8,1-1e-8)
        # Gamma multiplies posterior variance, never the linear mean update.
        # A bounded log-odds change keeps the A extrinsic variance positive.
        fraction_a=torch.sigmoid(torch.logit(analytic_fraction)+.5*torch.tanh(self.gamma_raw))
        fraction_a=fraction_a.clamp(1e-6,1-1e-6)
        calibrated=variance*fraction_a
        query,vb=extrinsic(post,calibrated,mean,variance)
        conditional,ell,alpha=self.nonlinear(query,vb)
        probability=torch.sigmoid(ell+torch.logit(activity_prior))
        estimate=probability[:,None,None,None]*conditional
        a=operator.reshape(operator.shape[0],-1)
        residual=y.reshape(len(a),-1)-a@pack(estimate)
        columns=residual.shape[1]
        raw=(residual.abs().square().sum()-residual.numel()*noise)/(columns*a.abs().square().sum())
        beta=torch.exp(self.beta_raw)
        # Smooth positivity for the residual proxy; its zero/negative value is
        # possible because the estimate depends on the observation noise.
        softness=.01*noise/(a.abs().square().sum()/len(a))
        positive=softness*F.softplus(raw/softness)
        requested=beta*positive
        ratio=requested/vb
        # A smooth bound keeps gradients for beta even when the residual proxy
        # is greater than the incoming variance. Hard clipping made beta dead.
        fraction_b=1e-4+(.95-1e-4)*ratio/(.95+ratio)
        tau=vb*fraction_b
        next_mean,next_variance=extrinsic(estimate,tau,query,vb)
        diagnostics=dict(query_variance=vb,linear_variance=calibrated,
            linear_variance_analytic=analytic,gamma=calibrated/analytic,
            alpha=alpha,beta=beta,raw_residual_variance=raw,
            posterior_variance=tau,requested_posterior_variance=requested,
            posterior_lower_bound=(requested/vb<1e-4),posterior_upper_bound=(requested/vb>.95),
            mean_activity=probability.mean(),maximum_activity=probability.max())
        return dict(estimate=estimate,conditional_mean=conditional,probabilities=probability,
                    logits=ell,next_mean=next_mean,next_variance=next_variance,diagnostics=diagnostics)


class UnfoldedReceiver(nn.Module):
    def __init__(self):
        super().__init__();self.layers=nn.ModuleList()

    def grow(self,score,activity,microbatch=8):
        self.layers.append(Layer(deepcopy(score),deepcopy(activity),microbatch).requires_grad_(True))

    def forward(self,y,operator,noise,activity_prior,initial_second_moment=1.0004404181394917):
        k,n=operator.shape[1:];m,r=y.shape[1:]
        mean=torch.zeros((k,m,r,n),dtype=y.dtype,device=y.device)
        variance=activity_prior*initial_second_moment
        outputs=[]
        for layer in self.layers:
            result=layer(y,operator,mean,variance,noise,activity_prior)
            outputs.append(result)
            mean,variance=result['next_mean'],result['next_variance']
        return outputs


def objective(outputs,truth,active,activity_prior):
    """Paper's layer-weighted NMSE plus the AFDM activity cross-entropy."""
    energy=truth.abs().square().sum()
    # Empty scenes remain in the training set; use expected prior energy there.
    denominator=torch.where(energy>0,energy,activity_prior*truth.numel())
    terms=[];nmse=[];bce=[]
    for i,out in enumerate(outputs):
        reconstruction=(out['estimate']-truth).abs().square().sum()/denominator
        activity=F.binary_cross_entropy_with_logits(out['logits']+torch.logit(activity_prior),active.double())
        weight=1. if i==len(outputs)-1 else .2
        terms.append(weight*(reconstruction+.1*activity))
        nmse.append(reconstruction);bce.append(activity)
    return sum(terms),dict(nmse=nmse,bce=bce)
