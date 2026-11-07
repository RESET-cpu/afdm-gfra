"""Frozen per-beam DnCNN followed by a learned joint-channel residual CNN.

This is a declared composite denoiser adaptation, not He's original network.
The whole map, including both CNN branches, participates in AMP derivatives.
"""
import json
from pathlib import Path
import sys
import numpy as np
import torch
from torch import nn
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.algorithm.baselines.ldamp.network import BeamDnCNN
from afdm_jadcedd.algorithm.baselines.ldamp.beam import capture_network,network_directions
from afdm_jadcedd.utils import sha256
from .model import JointDnCNN


class FrozenBeamBank(nn.Module):
    def __init__(self,directory):
        super().__init__();directory=Path(directory)
        self.manifest=json.loads((directory/'BANK.json').read_text())
        self.manifest_sha256=sha256(directory/'BANK.json')
        self.models=nn.ModuleList();self.scales=[]
        self.register_buffer('boundaries',torch.tensor(self.manifest['edges'][1:-1],dtype=torch.float32))
        for entry in self.manifest['entries']:
            path=directory/entry['path']
            if sha256(path)!=entry['sha256']:raise ValueError('Changed frozen bank')
            payload=torch.load(path,map_location='cpu',weights_only=True)
            model=BeamDnCNN(channels=2);model.load_state_dict(payload['model']);model.eval()
            for parameter in model.parameters():parameter.requires_grad_(False)
            self.models.append(model);self.scales.append(payload['recipe']['network_input_scale'])

    def train(self,mode=True):
        # The baseline bank remains frozen even during joint residual training.
        super().train(False);return self

    @staticmethod
    def beams(value):
        return torch.stack([value[...,:16,:,:],value[...,16:,:,:]],dim=-3).flatten(-5,-4)

    @staticmethod
    def channels(value,batch):
        value=value.reshape(*value.shape[:-4],batch,16,2,*value.shape[-2:])
        return torch.cat([value[...,0,:,:],value[...,1,:,:]],dim=-3)

    def forward(self,query,variance):
        batch=len(query);flat=self.beams(query);selected=torch.bucketize(variance.flatten(),self.boundaries)
        result=torch.empty_like(flat)
        for band,model in enumerate(self.models):
            idx=torch.nonzero(selected==band).flatten()
            if len(idx):result[idx]=model(flat[idx]/self.scales[band])*self.scales[band]
        return self.channels(result,batch)

    @torch.no_grad()
    def linearize(self,query,variance):
        batch=len(query);flat=self.beams(query);selected=torch.bucketize(variance.flatten(),self.boundaries)
        result=torch.empty_like(flat);cache=[]
        for band,model in enumerate(self.models):
            idx=torch.nonzero(selected==band).flatten()
            if len(idx):
                output,masks=capture_network(model,flat[idx]/self.scales[band])
                result[idx]=output*self.scales[band];cache.append((band,idx,masks))
        @torch.no_grad()
        def directions(delta):
            flat_delta=self.beams(delta);derivative=torch.empty_like(flat_delta)
            for band,idx,masks in cache:
                derivative[:,idx]=network_directions(self.models[band],flat_delta[:,idx]/self.scales[band],masks)*self.scales[band]
            return self.channels(derivative,batch)
        return self.channels(result,batch),directions


class ResidualJointDnCNN(JointDnCNN):
    def __init__(self,complex_power,bank,width=64,depth=20):
        super().__init__(complex_power,width=width,depth=depth)
        self.net[0]=nn.Conv2d(80,width,3,padding=1)
        self.bank=bank

    def forward(self,query,variance):
        base=self.bank(query,variance)
        ci,_,co,_=self.factors(variance)
        noise=(torch.log(variance)/4)[:,:,None,None].expand(-1,-1,*query.shape[-2:])
        features=torch.cat([ci*query,ci*base,noise],dim=1)
        return base+co*self.net(features)

    @torch.no_grad()
    def linearize_parts(self,query,variance):
        from torch.nn import functional as F
        if self.training:raise ValueError('Freeze BN for derivatives')
        base,base_directions=self.bank.linearize(query,variance)
        ci,_,co,_=self.factors(variance)
        noise=(torch.log(variance)/4)[:,:,None,None].expand(-1,-1,*query.shape[-2:])
        hidden=torch.cat([ci*query,ci*base,noise],dim=1);masks={}
        for index,layer in enumerate(self.net):
            hidden=layer(hidden)
            if isinstance(layer,nn.ReLU):masks[index]=hidden>0
        @torch.no_grad()
        def with_base(delta,bd):
            count,batch=delta.shape[:2]
            hidden=torch.cat([ci[None]*delta,ci[None]*bd,torch.zeros_like(delta[:,:,:16])],dim=2).flatten(0,1)
            for index,layer in enumerate(self.net):
                if isinstance(layer,nn.Conv2d):hidden=F.conv2d(hidden,layer.weight,None,padding=layer.padding)
                elif isinstance(layer,nn.BatchNorm2d):hidden=hidden*(layer.weight/torch.sqrt(layer.running_var+layer.eps))[None,:,None,None]
                elif isinstance(layer,nn.ReLU):hidden=(hidden.reshape(count,batch,*hidden.shape[1:])*masks[index][None]).flatten(0,1)
            return co[None]*hidden.reshape_as(delta)
        def correction_directions(delta):return with_base(delta,base_directions(delta))
        correction_directions.with_base=with_base
        return base+co*hidden,base_directions,correction_directions

    def linearize(self,query,variance):
        estimate,bd,cd=self.linearize_parts(query,variance)
        def directions(delta):
            base_delta=bd(delta)
            return base_delta+cd.with_base(delta,base_delta)
        return estimate,directions
