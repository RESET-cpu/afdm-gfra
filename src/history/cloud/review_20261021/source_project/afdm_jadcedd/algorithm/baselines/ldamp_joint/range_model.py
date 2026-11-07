"""Select trained denoiser outputs by each beam's public noise variance.

The original five-band DnCNN bank was trained up to complex variance 100.
Below that fixed boundary retain the learned joint residual adaptation; above
it use the independently trained, noise-conditioned joint DnCNN. Both networks
see the complete user query. Selection is fixed during partial derivatives,
as for the original bank. No truth, measured error, or zero-output fallback is
used in this function. This is a declared AFDM adaptation of noise-bank selection.
"""
import torch
from torch import nn


class RangeSelectedDnCNN(nn.Module):
    def __init__(self,low,high,boundary=100.):
        super().__init__();self.low=low;self.high=high;self.boundary=float(boundary)

    def masks(self,variance):
        high=variance>self.boundary
        high=torch.cat([high,high],dim=1)[:,:,None,None]
        return ~high,high

    def forward(self,query,variance):
        low,high=self.masks(variance)
        output=torch.zeros_like(query)
        if bool(low.any()):output+=self.low(query,variance)*low
        if bool(high.any()):output+=self.high(query,variance)*high
        return output

    @torch.no_grad()
    def linearize_parts(self,query,variance):
        low,high=self.masks(variance);output=torch.zeros_like(query);parts=[]
        def masked(derivative,mask):
            return lambda delta:derivative(delta)*mask[None]
        if bool(low.any()):
            estimate,base,correction=self.low.linearize_parts(query,variance)
            output+=estimate*low
            parts.extend([(16,masked(base,low)),(256,masked(correction,low))])
        if bool(high.any()):
            estimate,derivative=self.high.linearize(query,variance)
            output+=estimate*high
            parts.append((256,masked(derivative,high)))
        return output,parts

    def linearize(self,query,variance):
        low,high=self.masks(variance);output=torch.zeros_like(query);parts=[]
        if bool(low.any()):
            estimate,derivative=self.low.linearize(query,variance)
            output+=estimate*low;parts.append((derivative,low))
        if bool(high.any()):
            estimate,derivative=self.high.linearize(query,variance)
            output+=estimate*high;parts.append((derivative,high))
        def derivative(delta):return sum(part(delta)*mask[None] for part,mask in parts)
        return output,derivative


class MeanAndBeamSelectedDnCNN(RangeSelectedDnCNN):
    """Use the high-noise joint model for the entire high-mean-noise query.

    The high model's training bands are indexed by mean variance. Below the
    boundary, individual out-of-bank beams still use that model. This is a
    separately recorded development candidate, not a retrospective change to
    the original per-beam-only experiment.
    """
    def masks(self,variance):
        high=(variance>self.boundary)|(variance.mean(dim=1,keepdim=True)>self.boundary)
        high=torch.cat([high,high],dim=1)[:,:,None,None]
        return ~high,high
