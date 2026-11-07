"""Bounded CPU inspection of saved weights, no training or receiver experiment."""
from pathlib import Path
import hashlib
import io
import json
import sys
import time

import numpy as np
import torch
from threadpoolctl import threadpool_limits

from networks.score import DirectCaiConfig, DirectCaiNetwork
from project import ROOT, repository_path
from training.colored_score_20261024.model import ColoredScore
from training.colored_score_20261024.noise import Covariance, pack, unpack
from training.colored_score_20261024.formal_batches import draw_arrays, loss_from_score
from utils import sha256, write_json


def main():
    torch.set_num_threads(2)
    start = time.time()
    output = ROOT/'reference/colored_architecture_review_20261024'
    path = ROOT/'result/channel_denoising/data/colored_score_50000_matched_20261024/first_best.pt'
    raw = path.read_bytes()
    weight_hash = hashlib.sha256(raw).hexdigest()
    blob = torch.load(io.BytesIO(raw), map_location='cpu', weights_only=False)
    model = ColoredScore(DirectCaiNetwork(DirectCaiConfig(**blob['architecture']), order=1))
    model.load_state_dict(blob['state_dict']); model.eval()
    del raw
    config = json.loads((ROOT/'src/configs/training/colored_score_matched_20261024.json').read_text())
    binding = json.loads(repository_path(config['base_config']).read_text())
    prior = json.loads(repository_path(binding['prior_definition']).read_text())
    bank = np.load(repository_path(prior['data_files']['validation']), mmap_mode='r')
    identities = np.load(repository_path(prior['dataset_identities']['validation']['identities_path']))
    _, unique_rows = np.unique(identities[:, 0], return_index=True)
    rng = np.random.default_rng(20261024091)
    selected = rng.choice(unique_rows, size=64, replace=False)
    rows, saved = [], {}
    for index, limits in enumerate([(-20,-10),(-10,0),(0,10),(10,30)]):
        chosen = selected[index*16:(index+1)*16]
        arrays = draw_arrays(np.asarray(bank[chosen]), rng, np.random.default_rng(20261024092+index),
            config['scale'], dict(config['noise'], snr_db=limits))
        ts = tuple(torch.from_numpy(a) for a in arrays)
        h, r, v, ra, rc, _, _, _ = ts
        true = Covariance(v,ra,rc)
        unit = torch.eye(16,dtype=torch.complex64).expand_as(ra)
        conditions = dict(correct=true, shuffled=Covariance(v,ra.roll(1,0),rc.roll(1,0)),
            identity=Covariance(v,unit,unit))
        power = h.square().flatten(1).sum(1).numpy()
        results = {}
        with torch.inference_mode():
            for arm, condition in conditions.items():
                scores = torch.cat([model(r[j:j+4],Covariance(condition.variance[j:j+4],
                    condition.antenna[j:j+4],condition.column[j:j+4])) for j in range(0,16,4)])
                # Only the model's side information changes. Reconstruction and
                # scoring ALWAYS use the true C and original epsilon.
                mean = r + true.apply_real(scores)
                error = (mean-h).square().flatten(1).sum(1).numpy()
                results[arm] = dict(nmse_db=float(10*np.log10(error.sum()/power.sum())),
                    loss=float(loss_from_score(scores,ts)))
                saved[f'{index}_{arm}_errors'] = error
                if arm == 'correct':
                    correct = scores.clone()
                else:
                    results[arm]['score_relative_change'] = float((scores-correct).norm()/correct.norm())
            ea,qa=torch.linalg.eigh(ra); ec,qc=torch.linalg.eigh(rc)
            transformed=torch.einsum('bai,baoc,bcj->bioj',qa.conj(),unpack(r),qc.conj())
            factor=1/(1+v[:,None,None]*ea[:,:,None]*ec[:,None,:])
            estimate=pack(torch.einsum('bai,bioj,bcj->baoc',qa,transformed*factor[:,:,None,:],qc))
            error=(estimate-h).square().flatten(1).sum(1).numpy()
            results['isotropic_prior_linear_estimate']=dict(nmse_db=float(10*np.log10(error.sum()/power.sum())),
                assumed_complex_prior_covariance='I; surrogate, not measured true channel prior')
            results['zero_estimate']=dict(nmse_db=0.)
            results['noisy_input']=dict(nmse_db=float(10*np.log10((r-h).square().sum().item()/power.sum())))
        rows.append(dict(snr_db_interval=limits,samples=16,results=results))
        saved[f'{index}_signal_power']=power
        saved[f'{index}_rows']=chosen
        print(json.dumps(rows[-1]),flush=True)
    np.savez(output/'CONDITION_PROBE.npz',**saved)
    write_json(output/'CONDITION_PROBE.json',dict(scope='Exploratory saved-weight CPU diagnosis, 64 distinct development scenes; not the 1000-scene performance experiment or a significance test',
        checkpoint=str(path.relative_to(ROOT)),checkpoint_sha256=weight_hash,epoch=blob['metadata']['epoch'],
        script_sha256=sha256(Path(__file__)),seconds=time.time()-start,training_modified=False,rows=rows))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    with threadpool_limits(limits=2):
        main()
