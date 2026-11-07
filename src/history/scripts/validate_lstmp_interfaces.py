"""Algebra, interface and gradient checks only; no performance or training run."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import numpy as np
import torch
from threadpoolctl import threadpool_limits
from experiments.lstmp_candidate_20261019 import common,data,receiver
from experiments.lstmp_candidate_20261019.baseline_evaluation import binding


def state_hash(model):
    digest=hashlib.sha256()
    for name,tensor in model.state_dict().items():
        digest.update(name.encode());digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--device',default='cuda')
    parser.add_argument('--output',default='results/lstmp_interface_repair_20261019/INTERFACE_CHECKS.json')
    args=parser.parse_args()
    report_path=ROOT/args.output
    if report_path.exists():raise FileExistsError('Use a new output file to preserve prior checks')
    result=subprocess.run([sys.executable,'-m','pytest','tests/test_lstmp_candidate_interfaces.py','-q'],
        cwd=ROOT,capture_output=True,text=True)
    print(result.stdout,flush=True)
    if result.returncode:raise RuntimeError(result.stderr+result.stdout)
    threadpool_limits(4);torch.set_num_threads(4)
    checkpoint=ROOT/'tmp/mac_lstmp_assets_20261019/selected/AFDM_LSTMP/runs/lstmp_fresh_20261019/checkpoints/pretrain/last.pt'
    state=torch.load(checkpoint,map_location='cpu',weights_only=False)
    checkpoint_before=common.sha(checkpoint)
    torch.manual_seed(202610199200001)
    model=receiver.Receiver()
    for _ in range(5):model.add_layer(state['ema'])
    del state
    pointers=[{p.data_ptr() for p in layer.parameters()} for layer in model.layers]
    independent=all(not pointers[i]&pointers[j] for i in range(5) for j in range(i+1,5))
    model.to(args.device).train()
    before=state_hash(model)
    # Synthetic algebra fixture, not a physical recovery performance test.
    rng=np.random.default_rng(202610199200002)
    z=lambda shape:(rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2)
    a=z((16,2,16))/np.sqrt(32)
    values=dict(y=.1*z((16,16,16)),a=a,noise=.3,rho=.2)
    public,_=data.prepare_public(values,.5,args.device,phase_mode='known',noise_mode='known')
    labels=dict(x=common.real_tensor(.1*z((2,16,16,16)),args.device),
        active=torch.tensor([1.,0.],device=args.device))
    def forbid(*args,**kwargs):raise AssertionError('Optimizer update forbidden')
    with patch.object(torch.optim.Adam,'step',forbid),patch.object(torch.optim.AdamW,'step',forbid):
        outputs,diagnostics=model(public)
        value=receiver.loss(outputs,labels)
        if not torch.isfinite(value):raise AssertionError('Nonfinite synthetic loss')
        value.backward()
    gradients=[]
    for i,layer in enumerate(model.layers):
        entry=dict(layer=i+1,
            score_connected=any(p.grad is not None and bool((p.grad!=0).any()) for p in layer.score.parameters()),
            activity_connected=any(p.grad is not None and bool((p.grad!=0).any()) for p in layer.activity.parameters()),
            all_gradients_finite=all(p.grad is None or bool(torch.isfinite(p.grad).all()) for p in layer.parameters()),
            calibration_gradient=layer.calibration.grad.detach().cpu().tolist())
        assert entry['score_connected'] and entry['activity_connected'] and entry['all_gradients_finite']
        assert all(np.isfinite(entry['calibration_gradient']))
        gradients.append(entry)
    if any(entry['calibration_gradient'][2]==0 for entry in gradients[:4]):
        common.save_json(report_path.with_name('GRADIENT_CHECK_FAILURE.json'),
            dict(gradients=gradients,diagnostics=diagnostics,training_started=False,optimizer_updates=0))
        raise AssertionError('An intermediate beta is disconnected; see gradient failure record')
    assert gradients[-1]['calibration_gradient'][2]==0
    after=state_hash(model)
    assert independent and before==after and common.sha(checkpoint)==checkpoint_before
    original=ROOT/'tmp/mac_lstmp_review_20261019/AFDM_LSTMP'
    preservation=json.loads((ROOT/'results/lstmp_interface_repair_20261019/PRESERVATION_BEFORE.json').read_text())
    unchanged=all(common.sha(original/p)==h for p,h in preservation['source_files'].items())
    assert unchanged
    report=dict(status='PASS',scope='Algebra, dimensions, receipts, information boundary, metrics and synthetic backpropagation only',
        pytest=result.stdout.strip(),five_independent_layers=independent,gradients=gradients,
        candidate_state_unchanged=before==after,checkpoint_unchanged=True,original_mac_files_unchanged=unchanged,
        checkpoint_state_used='ema; incomplete pretraining, used only to exercise gradients',
        frozen_baseline_bindings=[binding(s)[1] for s in common.CONFIG['baseline_comparisons']],
        source_hashes={str(p.relative_to(ROOT)):common.sha(p) for p in
            (ROOT/'experiments/lstmp_candidate_20261019').rglob('*') if p.is_file() and p.suffix in ('.py','.json')},
        training_started=False,optimizer_updates=0,trained_receiver_stability='NOT_EVALUATED',
        actual_estimated_frontend_interface='Four paired physical inputs in validation/ROWS.json; no performance acceptance',
        generated_at_unix=time.time())
    common.save_json(report_path,report)
    print(json.dumps({k:report[k] for k in ('status','five_independent_layers','candidate_state_unchanged',
        'training_started','optimizer_updates','trained_receiver_stability')},indent=2))


if __name__=='__main__':main()
