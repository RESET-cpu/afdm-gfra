"""Frozen per-beam DnCNNs in an invertible full AFDM channel representation.

Input beam queries stay in normalized AFDM coordinates. Covariance is frozen
during each MC perturbation. Only its per-beam average diagonal selects a noise
interval: this approximation does not whiten correlated effective errors.
"""
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as functional
from .network import BeamDnCNN
from .representation import Representation


def capture_network(model,value):
    """Evaluate frozen DnCNN and retain only its ReLU masks for derivatives."""
    hidden=value;masks={}
    for index,layer in enumerate(model.noise):
        hidden=layer(hidden)
        if isinstance(layer,nn.ReLU):masks[index]=hidden>0
    return value-hidden,masks


def network_directions(model,directions,masks):
    """Exact real directional derivatives of frozen Conv/BN/ReLU layers.

    directions has shape [directions,batch,channels,height,width]. Biases and
    BN offsets have zero derivative; ReLU uses the same zero-at-zero convention
    as PyTorch autograd. No stochastic derivative or finite difference here.
    """
    count,batch=directions.shape[:2];hidden=directions.flatten(0,1)
    for index,layer in enumerate(model.noise):
        if isinstance(layer,nn.Conv2d):
            hidden=functional.conv2d(hidden,layer.weight,None,layer.stride,layer.padding,layer.dilation,layer.groups)
        elif isinstance(layer,nn.BatchNorm2d):
            factor=layer.weight/torch.sqrt(layer.running_var+layer.eps)
            hidden=hidden*factor[None,:,None,None]
        elif isinstance(layer,nn.ReLU):
            hidden=(hidden.reshape(count,batch,*hidden.shape[1:])*masks[index][None]).flatten(0,1)
        else:raise TypeError('Unrecognized frozen DnCNN layer')
    return directions-hidden.reshape_as(directions)


class BeamDenoiser:
    def __init__(self,directory,device='mps',batch_size=128,allow_incomplete=False):
        self.directory=Path(directory);self.device=device;self.batch_size=batch_size
        self.manifest=json.loads((self.directory/'BANK.json').read_text())
        if not self.manifest['complete'] and not allow_incomplete:raise ValueError('Incomplete noise bank')
        self.scale=self.manifest['scale'];self.representation=Representation();self.models={};self.input_scales={}
        self.entries={entry['index']:entry for entry in self.manifest['entries']}
        for index,entry in self.entries.items():
            path=self.directory/entry['path']
            if hashlib.sha256(path.read_bytes()).hexdigest()!=entry['sha256']:raise ValueError('Changed checkpoint')
            payload=torch.load(path,map_location='cpu',weights_only=True)
            if payload['variant']['channels']!=2 or payload['recipe']['representation']!='beam_time_lag_dft':
                raise ValueError('Incompatible denoiser checkpoint')
            model=BeamDnCNN(channels=2).to(device);model.load_state_dict(payload['model']);model.eval()
            for parameter in model.parameters():parameter.requires_grad_(False)
            self.models[index]=model;self.input_scales[index]=payload['recipe']['network_input_scale']
        self.selection_log=[]

    @torch.inference_mode()
    def linearize(self,query,covariance):
        """Return the output and an exact real-directional-derivative closure.

        The same interval, fixed scales, weights and ReLU masks are used for
        all directions. The partial trace still uses Monte Carlo probes.
        """
        query=np.asarray(query);k,m,r,n=query.shape
        variance,selected=self.select(covariance)
        coefficients=self.representation.forward(query);estimate=np.empty_like(coefficients);caches=[]
        for index in np.unique(selected):
            beams=np.flatnonzero(selected==index);scale=self.input_scales[int(index)]
            gain=self.entries[int(index)].get('output_scale',1.);model=self.models[int(index)]
            value=coefficients[:,beams].reshape(-1,r,n)
            packed=np.stack([value.real,value.imag],axis=1).astype(np.float32)/scale
            outputs=[];chunks=[]
            for start in range(0,len(packed),self.batch_size):
                stop=min(start+self.batch_size,len(packed))
                output,masks=capture_network(model,torch.from_numpy(packed[start:stop]).to(self.device))
                outputs.append(output.cpu().numpy());chunks.append((start,stop,masks))
            prediction=np.concatenate(outputs)*scale*gain
            estimate[:,beams]=(prediction[:,0]+1j*prediction[:,1]).reshape(k,len(beams),r,n)
            caches.append((beams,scale,gain,model,chunks))
        self.selection_log.append(dict(variances=variance.tolist(),intervals=selected.tolist()))

        @torch.inference_mode()
        def directions(delta):
            delta=np.asarray(delta)
            if delta.ndim!=5 or delta.shape[1:]!=query.shape:raise ValueError('Direction shape mismatch')
            transformed=self.representation.forward(delta);count=len(delta);result=np.empty_like(transformed)
            for beams,scale,gain,model,chunks in caches:
                value=transformed[:,:,beams].reshape(count,-1,r,n)
                packed=np.stack([value.real,value.imag],axis=2).astype(np.float32)/scale
                outputs=[]
                for start,stop,masks in chunks:
                    output=network_directions(model,torch.from_numpy(packed[:,start:stop]).to(self.device),masks)
                    outputs.append(output.cpu().numpy())
                prediction=np.concatenate(outputs,axis=1)*scale*gain
                result[:,:,beams]=(prediction[:,:,0]+1j*prediction[:,:,1]).reshape(count,k,len(beams),r,n)
            return self.representation.inverse(result)
        return self.representation.inverse(estimate),directions

    def select(self,covariance):
        diagonal=np.diag(covariance).real
        if diagonal.size!=256:raise ValueError('Declared AFDM/array dimensions required')
        variances=diagonal.reshape(16,16).mean(axis=1)
        edges=np.array(self.manifest['edges'])
        selected=np.searchsorted(edges[1:-1],variances,side='left')
        if any(int(index) not in self.models for index in selected):
            raise ValueError(f'Missing selected interval: {selected.tolist()}')
        return variances,selected

    @torch.inference_mode()
    def __call__(self,query,covariance):
        query=np.asarray(query);k,m,r,n=query.shape
        if (m,r,n)!=(16,16,16):raise ValueError('Declared AFDM/array dimensions required')
        variance,selected=self.select(covariance)
        coefficients=self.representation.forward(query)
        estimate=np.empty_like(coefficients)
        for index in np.unique(selected):
            beams=np.flatnonzero(selected==index);scale=self.input_scales[int(index)]
            value=coefficients[:,beams].reshape(-1,r,n)
            packed=np.stack([value.real,value.imag],axis=1).astype(np.float32)/scale
            outputs=[]
            for start in range(0,len(packed),self.batch_size):
                outputs.append(self.models[int(index)](torch.from_numpy(packed[start:start+self.batch_size]).to(self.device)).cpu().numpy())
            prediction=np.concatenate(outputs)*scale*self.entries[int(index)].get('output_scale',1.)
            estimate[:,beams]=(prediction[:,0]+1j*prediction[:,1]).reshape(k,len(beams),r,n)
        self.selection_log.append(dict(variances=variance.tolist(),intervals=selected.tolist()))
        return self.representation.inverse(estimate)
