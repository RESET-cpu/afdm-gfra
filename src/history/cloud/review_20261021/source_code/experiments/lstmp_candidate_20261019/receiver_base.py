"""L-STMP-inspired AFDM receiver: general A, independent scores, new activity heads.

The activity head and smooth variance safeguards are project adaptations.
Residual variance is an iteration parameter, not an exact posterior MSE.
"""
import math, time
import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.checkpoint import checkpoint
from .backbone import make_score
from .common import CONFIG, check_budget
from .data import pack, unpack


class ActivityHead(nn.Module):
    def __init__(self):
        super().__init__()
        self.maps = nn.Sequential(nn.Conv2d(64,32,3,padding=1),nn.SiLU(),
                                  nn.Conv2d(32,64,3,stride=2,padding=1),nn.SiLU(),
                                  nn.Conv2d(64,64,3,stride=2,padding=1),nn.SiLU(),nn.AdaptiveAvgPool2d(1))
        self.head = nn.Sequential(nn.Linear(69,64),nn.SiLU(),nn.Linear(64,1))
        nn.init.zeros_(self.head[-1].weight); nn.init.zeros_(self.head[-1].bias)

    def forward(self, r, v, mean, rho):
        x, f = r.flatten(1,2), mean.flatten(1,2)
        maps = torch.cat((x,f),dim=1) / torch.sqrt(1+v)[:,None,None,None]
        energy = lambda t: 2*t.square().flatten(1).mean(1)
        scalars = torch.stack((torch.log(v), torch.log1p(energy(x)/v),
                               torch.log1p(energy(f)/v),torch.log1p(energy(x-f)/v),
                               torch.full_like(v,math.log(rho/(1-rho)))),dim=1)
        # This is a directly supervised posterior classifier, not an AWGN likelihood-ratio identity.
        return self.head(torch.cat((self.maps(maps).flatten(1),scalars),dim=1))[:,0] + math.log(rho/(1-rho))


class Layer(nn.Module):
    def __init__(self, initial_score=None):
        super().__init__()
        self.score = make_score()
        if initial_score is not None: self.score.load_state_dict(initial_score)
        self.activity = ActivityHead()
        self.calibration = nn.Parameter(torch.zeros(3))


def _linear_terms(public, prior, variance):
    s, noise = public['s'], public['noise']
    gain = s*variance/(noise+s.square()*variance)
    residual = public['y']-public['a']@pack(prior)
    correction = unpack(public['vv']@(gain.repeat(2)[:,None]*(public['uh']@residual)),prior.shape)
    unknowns = public['a'].shape[1]//2
    # Trace over all complex unknowns, including the null space. This form also
    # avoids cancellation for a full-column-rank operator at high SNR.
    posterior_fraction = ((unknowns-len(s))+(noise/(noise+s.square()*variance)).sum())/unknowns
    information_fraction = (s*gain).sum()/unknowns
    return correction,posterior_fraction,information_fraction


def linear_update(public, prior, variance):
    correction,fraction,_=_linear_terms(public,prior,variance)
    return prior+correction,variance*fraction


def linear_query(public, prior, variance, log_gamma):
    """Same calibrated Gaussian extrinsic equations, without subtracting 1-g.

    Computing the information fraction directly avoids catastrophic cancellation
    when a tiny incoming variance makes the posterior/prior ratio round to one.
    """
    correction,posterior_fraction,information_fraction=_linear_terms(public,prior,variance)
    quotient=torch.exp(log_gamma)*posterior_fraction/information_fraction
    return prior+(1+quotient)*correction,variance*quotient,variance*posterior_fraction


def feedback_variance(raw, query_variance, log_beta, *, order='after_positive'):
    """Learn a positive scale after positive mapping (project parameterization).

    The residual is an iteration parameter, not an unbiased posterior MSE.
    `before_positive` exists only for paired regression against the Mac source.
    """
    temperature = CONFIG['receiver']['variance_soft_floor_temperature_ratio']*query_variance
    if order=='after_positive':
        positive = torch.exp(log_beta)*(temperature*F.softplus(raw/temperature)+1e-6)
    elif order=='before_positive':
        positive = temperature*F.softplus(torch.exp(log_beta)*raw/temperature)+1e-6
    else:
        raise ValueError('Unknown variance calibration order')
    ceiling = CONFIG['receiver']['maximum_feedback_variance_ratio']
    if order=='before_positive':
        ratio=(ceiling*torch.tanh(positive/(ceiling*query_variance))).clamp_min(1e-6)
    else:
        # A smooth lower bound preserves the beta gradient when the residual is
        # very negative. A hard clamp here disconnected beta in a regression.
        lower=1e-6
        ratio=lower+(ceiling-lower)*torch.tanh(positive/((ceiling-lower)*query_variance))
    return query_variance*ratio,ratio


class Receiver(nn.Module):
    def __init__(self, *, variance_calibration_order='after_positive'):
        super().__init__(); self.layers = nn.ModuleList()
        self.use_checkpoint = True
        self.checkpoint_first_layers = 0
        self.checkpoint_min_users = 0
        self.variance_calibration_order = variance_calibration_order

    def add_layer(self, initial_score):
        self.layers.append(Layer(initial_score))

    def score_call(self, model, x, v):
        values = []
        selected = (self.checkpoint_first_layers > 0 and len(x) >= self.checkpoint_min_users and
                    any(model is layer.score for layer in self.layers[:self.checkpoint_first_layers]))
        recompute = self.use_checkpoint or selected
        for begin in range(0,len(x),CONFIG['receiver']['microbatch']):
            args = (x[begin:begin+CONFIG['receiver']['microbatch']],v[begin:begin+CONFIG['receiver']['microbatch']])
            values.append(checkpoint(model,*args,use_reentrant=False) if recompute and torch.is_grad_enabled() else model(*args))
        return torch.cat(values)

    def forward(self, public, *, return_messages=False):
        y, a, rho = public['y'], public['a'], public['rho']
        prior = y.new_zeros(public['channel_shape'])
        variance = y.new_tensor(rho*CONFIG.get('normalized_training_second_moment',1.))
        outputs, diagnostics, messages = [], [], []
        for layer in self.layers:
            c = layer.calibration
            r,v,analytical_v=linear_query(public,prior,variance,c[0])
            nv = v.expand(len(r))
            score = self.score_call(layer.score,r,nv)
            conditional = r+torch.exp(c[1])*v/2*score
            logits = layer.activity(r,nv,conditional,rho)
            probability = torch.sigmoid(logits)
            estimate = probability[:,None,None,None,None]*conditional
            residual = y-a@pack(estimate)
            # Real block energy equals complex residual energy; ||A_real||² = 2||A||².
            frames,columns = y.shape[0]//2,y.shape[1]
            raw = (residual.square().sum()-frames*columns*public['noise'])/(columns*a.square().sum()/2)
            ceiling = CONFIG['receiver']['maximum_feedback_variance_ratio']
            post_v,feedback_ratio = feedback_variance(raw,v,c[2],order=self.variance_calibration_order)
            prior = (estimate-feedback_ratio*r)/(1-feedback_ratio)
            variance = post_v/(1-feedback_ratio)
            outputs.append((estimate,logits))
            diagnostics.append(dict(query_variance=float(v.detach()),raw_residual_variance=float(raw.detach()),
                feedback_variance=float(post_v.detach()),negative_raw_variance=bool(raw.detach()<0),
                feedback_ratio=float(feedback_ratio.detach()),next_variance=float(variance.detach()),
                partial_feedback_mean_gain=float(1/(1-feedback_ratio.detach())),
                linear_variance=float(analytical_v.detach()),score_log_scale=float(c[1].detach()),
                feedback_log_scale=float(c[2].detach()),
                out_of_pretraining_support=not(CONFIG['complex_variance_support'][0]<=float(v.detach())<=CONFIG['complex_variance_support'][1]),
                ratio_near_ceiling=bool(feedback_ratio.detach()>.99*ceiling)))
            if return_messages:
                messages.append(dict(query=r.detach(),conditional=conditional.detach(),next_prior=prior.detach()))
        return (outputs,diagnostics,messages) if return_messages else (outputs,diagnostics)


def loss(outputs, labels):
    denom = labels['x'].square().sum().clamp_min(1e-8)
    terms = [(x-labels['x']).square().sum()/denom + CONFIG['receiver']['activity_loss_weight']*
             F.binary_cross_entropy_with_logits(logits,labels['active']) for x,logits in outputs]
    auxiliary = CONFIG['receiver']['earlier_layer_loss_weight']
    if 'auxiliary_total_weight' in CONFIG['receiver'] and len(terms) > 1:
        auxiliary = CONFIG['receiver']['auxiliary_total_weight'] / (len(terms)-1)
    return (sum(auxiliary*x for x in terms[:-1])+terms[-1])/(1+auxiliary*(len(terms)-1))


def metrics(outputs, labels):
    x, logits = outputs[-1]; p = torch.sigmoid(logits)
    active = labels['active'].bool(); decision = p>=CONFIG['receiver']['activity_threshold']
    error=(x.detach().double()-labels['x'].double()).square()
    energy=labels['x'].double().square()
    scale2=labels.get('physical_scale',1.)**2
    total_error=float(error.sum())*scale2; total_energy=float(energy.sum())*scale2
    return dict(nmse=total_error/total_energy if total_energy>0 else None,
                activity_bce=float(F.binary_cross_entropy_with_logits(logits.detach(),labels['active'])),
                error_energy=total_error,truth_energy=total_energy,
                active_error_energy=float(error[active].sum())*scale2,
                active_truth_energy=float(energy[active].sum())*scale2,
                inactive_error_energy=float(error[~active].sum())*scale2,
                complex_coefficients=x.numel()//2,
                misses=int((active & ~decision).sum()),false_alarms=int((~active & decision).sum()),
                active=int(active.sum()),inactive=int((~active).sum()))


def synchronize(device):
    device = torch.device(device)
    if device.type == 'cuda': torch.cuda.synchronize(device)
    elif device.type == 'mps': torch.mps.synchronize()


def summarize_rows(rows):
    if not rows: raise ValueError('Cannot summarize an empty evaluation')
    ratios=[row['nmse'] for row in rows if row['nmse'] is not None]
    totals={k:sum(row[k] for row in rows) for k in ('error_energy','truth_energy',
        'active_error_energy','active_truth_energy','inactive_error_energy',
        'complex_coefficients','misses','false_alarms','active','inactive')}
    divide=lambda a,b:a/b if b else None
    db=lambda value:10*math.log10(value) if value is not None and value>0 else None
    pooled=divide(totals['error_energy'],totals['truth_energy'])
    mean=sum(ratios)/len(ratios) if ratios else None
    summary=dict(scenes=len(rows),**totals,pooled_nmse=pooled,pooled_nmse_db=db(pooled),
        active_nmse=divide(totals['active_error_energy'],totals['active_truth_energy']),
        active_nmse_db=db(divide(totals['active_error_energy'],totals['active_truth_energy'])),
        mean_scene_nmse=mean,mean_scene_nmse_db=db(mean),zero_truth_energy_scenes=len(rows)-len(ratios),
        aer=divide(totals['misses']+totals['false_alarms'],totals['active']+totals['inactive']),
        missed_detection_rate=divide(totals['misses'],totals['active']),
        false_alarm_rate=divide(totals['false_alarms'],totals['inactive']))
    if all('loss' in row for row in rows): summary['loss']=sum(row['loss'] for row in rows)/len(rows)
    if all('activity_bce' in row for row in rows):
        summary['mean_scene_activity_bce']=sum(row['activity_bce'] for row in rows)/len(rows)
    for key in ('preparation_seconds','inference_seconds','total_seconds'):
        if all(key in row for row in rows): summary['mean_'+key]=sum(row[key] for row in rows)/len(rows)
    return summary


def summarize_conditions(rows):
    groups={}
    for row in rows:
        condition=dict(row.get('condition',{}),snr_db=row['snr'])
        key=tuple(sorted(condition.items()))
        groups.setdefault(key,[]).append(row)
    return [dict(condition=dict(key),**summarize_rows(group)) for key,group in groups.items()]


def evaluate(model, cases, *, started=None, rows=None, on_row=None):
    model.eval(); rows=[] if rows is None else list(rows)
    with torch.no_grad():
        for index in range(len(rows),len(cases)):
            if started is not None: check_budget(started)
            synchronize(cases.device)
            before=time.perf_counter()
            public, labels, info = cases[index]
            synchronize(cases.device)
            ready=time.perf_counter()
            outputs, diagnostics, messages = model(public,return_messages=True)
            synchronize(cases.device)
            finished=time.perf_counter()
            row=dict(**info,case_index=index,loss=float(loss(outputs,labels)),**metrics(outputs,labels),diagnostics=diagnostics,
                     layer_metrics=[metrics([output],labels) for output in outputs],
                     preparation_seconds=ready-before,inference_seconds=finished-ready,total_seconds=finished-before)
            truth=labels['x']; active=labels['active'].bool()
            for diag,message in zip(diagnostics,messages):
                error=(message['query']-truth).square()
                diag.update(query_mse=float(2*error.mean()),
                    query_active_mse=float(2*error[active].mean()) if active.any() else None,
                    query_inactive_mse=float(2*error[~active].mean()) if (~active).any() else None)
            if not math.isfinite(row['loss']) or not math.isfinite(row['nmse']):
                raise FloatingPointError('Nonfinite evaluation; case retained')
            rows.append(row)
            if on_row is not None: on_row(rows)
    return dict(summary=summarize_rows(rows),by_condition=summarize_conditions(rows),
        layer_summary=[dict(layer=i+1,**summarize_rows([row['layer_metrics'][i] for row in rows]))
                       for i in range(len(rows[0]['layer_metrics']))],rows=rows)
