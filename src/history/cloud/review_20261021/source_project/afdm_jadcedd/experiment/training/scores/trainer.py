"""Shared validation, batches and device state for first-score training."""
import json
import os
from pathlib import Path
import time
import numpy as np
import torch
from .score_matching import make_cai_batch
from .direct_objectives import direct_first_loss, direct_second_loss
from .device import restore_device_rng
from afdm_jadcedd.utils import write_json


def cpu_state(model):
    return {k: v.detach().cpu().clone() for k, v in model.state_dict().items()}


class ScoreTrainer:
    def __init__(self, output, *, device='mps'):
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.device = str(device)
        if torch.device(self.device).type not in ('cpu', 'mps', 'cuda'):
            raise ValueError('supported training devices: cpu, mps, cuda')
        self.stop = False

    def request_stop(self, *_):
        self.stop = True

    def status(self, state, **kwargs):
        row = dict(status=state, pid=os.getpid(), updated_unix=time.time(), **kwargs)
        write_json(self.output/'status.json', row)
        print(json.dumps(row), flush=True)

    def device_rng(self):
        return torch.mps.get_rng_state().cpu() if self.device == 'mps' else None

    def restore_device_rng(self, state):
        restore_device_rng(self.device, state)

    def validation(self, model, first, data, cfg, order):
        settings = cfg['training']
        continuous = settings['architecture'].get('noise_conditioning', 'discrete') == 'continuous'
        rng = np.random.default_rng(settings['validation_seed'])
        total = count = error = power = risk = 0
        negative_coordinates = nonpositive_sample_traces = 0
        bands = {}; model.eval()
        with torch.inference_mode():
            for start in range(0, len(data), settings['microbatch_size']):
                h, r, v, labels = self.make_batch(data[start:start+settings['microbatch_size']], rng, cfg)
                ht, rt, vt = [torch.as_tensor(x, device=self.device) for x in (h, r, v)]
                lt = torch.as_tensor(labels, dtype=torch.float32 if continuous else torch.long,
                                     device=self.device); vr = vt[:, None]/2
                if order == 'first':
                    s1 = model(rt, lt); mu = rt+vr*s1; q = torch.zeros_like(mu)
                    loss = direct_first_loss(s1, rt, ht, vt)
                else:
                    s1 = first(rt, lt); s2 = model(rt, lt)
                    mu = rt+vr*s1; q = vr+vr.square()*s2
                    loss = direct_second_loss(s2, s1, rt, ht, vt)
                e = (mu-ht).square().flatten(1).sum(1).cpu().numpy().astype(float)
                s = ht.square().flatten(1).sum(1).cpu().numpy().astype(float)
                t = q.flatten(1).sum(1).cpu().numpy().astype(float)
                if order == 'second':
                    negative_coordinates += int((q < 0).sum().cpu())
                    nonpositive_sample_traces += int(np.sum(t <= 0))
                total += float(loss.cpu())*len(h); count += len(h)
                error += e.sum(); power += s.sum(); risk += t.sum()
                # Bins summarize validation ONLY; network conditions above
                # remain continuous, including for samples inside each bin.
                groups = np.floor(-10*np.log10(labels)/5)*5 if continuous else labels
                for label in np.unique(groups):
                    mask = groups == label
                    key = f'snr_{int(label)}_to_{int(label)+5}_db' if continuous else str(int(label))
                    row = bands.setdefault(key, dict(samples=0, error=0., signal=0., reported=0.))
                    row['samples'] += int(mask.sum()); row['error'] += float(e[mask].sum())
                    row['signal'] += float(s[mask].sum()); row['reported'] += float(t[mask].sum())
        for row in bands.values():
            row['nmse_db'] = float(10*np.log10(row['error']/row['signal']))
            row['error_to_reported'] = row['error']/row['reported'] if row['reported'] else None
        return dict(loss=total/count, samples=count, nmse_db=float(10*np.log10(error/power)),
                    error=float(error), reported=float(risk), error_to_reported=float(error/risk) if risk else None,
                    raw_negative_variance_coordinates=negative_coordinates,
                    raw_nonpositive_sample_variance_traces=nonpositive_sample_traces,
                    bands=bands)

    @staticmethod
    def make_batch(channels, rng, cfg):
        architecture = cfg['training']['architecture']
        return make_cai_batch(channels, rng, cfg['scores']['global_complex_rms'],
            normalization=cfg['scores'].get('normalization', 'population_rms'),
            snr_db_min=architecture.get('snr_db_min', -10),
            snr_db_max=architecture.get('snr_db_max', 30),
            noise_conditioning=architecture.get('noise_conditioning', 'discrete'))

