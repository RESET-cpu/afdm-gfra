"""Full activity-times-score mean and its real directional derivatives.

The noise label is held fixed. Unlike training's detached score features, the
inference Jacobian includes the classifier's dependence on the score mean.
The original networks and their training implementation remain untouched.
"""
import numpy as np
import torch
from afdm_jadcedd.algorithm.score_amp.denoiser import FrozenJointDenoiser
from afdm_jadcedd.algorithm.score_amp.core import UnsupportedVariance
from afdm_jadcedd.algorithm.baselines.ldamp.representation import beam_transform


def evidence_logits(network, observation, variance, mean):
    """Same frozen feature values as EvidenceNetwork, with the full chain rule."""
    k=len(observation);x=observation.reshape(k,2*network.config.antennas,network.config.side,network.config.side)
    f=mean.reshape_as(x) if network.config.use_score_mean else torch.zeros_like(x)
    factor=torch.sqrt(2/(1+variance))[:,None,None,None]
    maps=torch.cat((factor*x,factor*f),dim=1)
    rx=2*x.square().flatten(1).mean(1)/variance
    ff=2*f.square().flatten(1).mean(1)/variance
    rf=2*(x*f).flatten(1).mean(1)/variance
    residual=2*(x-f).square().flatten(1).mean(1)/variance
    scalar=torch.stack((torch.log(variance)/5,torch.log1p(rx),torch.log1p(ff),
                        torch.sign(rf)*torch.log1p(abs(rf)),torch.log1p(residual)),dim=1)
    condition=network.condition(scalar[:,:1])
    for block,bias in zip(network.blocks,network.biases):
        maps=block(maps)+bias(condition)[:,:,None,None]
    return network.readout(torch.cat((maps.flatten(1),scalar),dim=1))[:,0]


class ScoreDenoiser:
    def __init__(self,binding,*,activity_prior,device='cpu',batch_size=8):
        self.frozen=FrozenJointDenoiser(binding,device=device,batch_size=batch_size)
        self.scale=self.frozen.scale;self.noise_support=self.frozen.noise_support
        if not 0<activity_prior<1:raise ValueError('Public activity prior required')
        self.activity_prior=float(activity_prior);self.device=device;self.batch_size=batch_size
        self.calls=self.direction_evaluations=0;self.last_probabilities=None

    def components(self,x,v):
        f=x+(v[:,None,None,None,None]/2)*self.frozen.first(x,v)
        logits=evidence_logits(self.frozen.evidence.network,x,v,f)
        p=torch.sigmoid(logits+float(np.log(self.activity_prior)-np.log1p(-self.activity_prior)))
        return f,p

    def mapping(self,x,v):
        f,p=self.components(x,v)
        return p[:,None,None,None,None]*f

    def _pack(self,x):
        return torch.as_tensor(np.stack((x.real,x.imag),axis=1),dtype=torch.float32,device=self.device)

    def infer(self,query,covariance):
        query=np.asarray(query);v=float(np.trace(covariance).real/covariance.shape[0])
        if not self.noise_support[0]<=v<=self.noise_support[1]:
            raise UnsupportedVariance(f'Query variance {v:.12g} outside {self.noise_support}')
        physical=beam_transform(query,inverse=True);means=[];probabilities=[]
        with torch.no_grad():
            for start in range(0,len(query),self.batch_size):
                xb=self._pack(physical[start:start+self.batch_size]);vb=torch.full((len(xb),),v,device=self.device)
                f,p=self.components(xb,vb);means.append(f.cpu().numpy().astype(float));probabilities.append(p.cpu().numpy().astype(float))
        packed=np.concatenate(means);p=np.concatenate(probabilities);f=packed[:,0]+1j*packed[:,1]
        self.calls+=1;self.last_probabilities=p
        return dict(output=beam_transform(p[:,None,None,None]*f),conditional_mean=beam_transform(f),
                    probabilities=p,variance=v)

    def linearize(self,query,covariance):
        result=self.infer(query,covariance);physical=beam_transform(query,inverse=True);v=result['variance']
        def directions(delta):
            delta=np.asarray(delta)
            if delta.ndim!=5 or delta.shape[1:]!=query.shape:raise ValueError('Direction shape mismatch')
            values=[]
            for direction in delta:
                physical_direction=beam_transform(direction,inverse=True);blocks=[]
                for start in range(0,len(query),self.batch_size):
                    xb=self._pack(physical[start:start+self.batch_size]);db=self._pack(physical_direction[start:start+self.batch_size])
                    vb=torch.full((len(xb),),v,device=self.device)
                    # Forward AD differentiates score, feature construction,
                    # activity probability, and their product in one mapping.
                    _,jvp=torch.func.jvp(lambda x:self.mapping(x,vb),(xb,),(db,))
                    blocks.append(jvp.detach().cpu().numpy().astype(float))
                packed=np.concatenate(blocks)
                values.append(beam_transform(packed[:,0]+1j*packed[:,1]))
                self.direction_evaluations+=1
            return np.stack(values)
        return result['output'],directions
