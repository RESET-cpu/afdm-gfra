"""One calibrated posterior readout after unchanged C-STMP iterations."""
import time
import numpy as np
from scipy.special import expit,logit
from algorithm.C_STMP_retrained.receiver import Receiver as FrozenReceiver


class Receiver(FrozenReceiver):
    def infer(self, inputs, *, observer=None):
        last={}
        def capture(row,state,r,v,*args):
            last.clear();last.update(r=r.copy(),reported_variance=float(np.trace(v).real/len(v)))
            if observer is not None:observer(row,state,r,v,*args)
        arrays,record=super().infer(inputs,observer=capture)
        started=time.perf_counter();r=last['r'];k,m,nr,nc=r.shape
        variance=float(np.median(np.mean(abs(r)**2,axis=(1,2,3))))
        support=self.model.noise_support
        info=dict(estimator='median_k mean(abs(r_k)^2)',variance=variance,
            original_reported_variance=last['reported_variance'],feedback=False,
            original_probabilities=arrays['probabilities'].tolist(),
            original_estimate_sha256=None,receiver_truth_used=False)
        if not support[0]<=variance<=support[1]:
            record['final_readout']=dict(info,status='OUTSIDE_TRAINING_SUPPORT_ORIGINAL_OUTPUT_RETAINED')
            return arrays,record
        before=self.model.network_samples,self.model.first_calls
        moments=self.model.infer(r,np.full(k,variance))
        mean=moments.mean
        logits=self.evidence.infer(r,np.full(k,variance),mean)
        probability=expit(logit(inputs.activity_prior)+logits-logit(self.evidence.training_class_prior))
        raw_tau=float(np.mean(moments.variance))
        tau=max(raw_tau,self.configuration['conditional_variance_floor_checkpoint_normalized'])
        flat=mean.reshape(k,m,-1)
        gram=flat@flat.conj().swapaxes(-1,-2)/(nr*nc)
        covariance=probability[:,None,None]*tau*np.eye(m)+(probability*(1-probability))[:,None,None]*gram
        scale=self.configuration['scale']
        arrays.update(estimate=probability[:,None,None,None]*mean*scale,conditional_matrix=mean*scale,
            probabilities=probability,activity_decision=probability>=self.configuration['decision_threshold'],
            spatial_covariance=covariance*scale**2)
        if not all(np.isfinite(a).all() for a in arrays.values()):raise FloatingPointError('Invalid calibrated posterior readout')
        elapsed=time.perf_counter()-started
        record.update(candidate='final_query_power_readout',seconds=record['seconds']+elapsed)
        record['first_network_samples']+=self.model.network_samples-before[0]
        record['first_score_calls']+=self.model.first_calls-before[1]
        record['first_score_samples']+=k;record['first_mean_samples']+=k
        record['classifier_calls']+=1;record['classifier_samples']+=k
        record['activity_evidence_calls']+=1;record['activity_evidence_samples']+=k
        record['final_readout']=dict(info,status='APPLIED',conditional_variance_raw=raw_tau,
            conditional_variance_used=tau,raw_per_user_variance=moments.variance.tolist(),
            probabilities=probability.tolist(),seconds=elapsed,additional_first_calls=self.model.first_calls-before[1],
            note='Final posterior recomputation only. Original iterations, stopping trace and feedback are unchanged.')
        return arrays,record
