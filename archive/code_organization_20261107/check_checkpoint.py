"""One synthetic AWGN query through both copies of the frozen pretrained mean."""
import gc
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'src'))
import numpy as np
import torch
from algorithm.GP_MP.denoising import Denoiser as Original
from afdm_gfra.receiver.gp_mp.denoising import Denoiser as Organized

torch.set_num_threads(2)
torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False
torch.backends.cudnn.benchmark = False
device = 'cuda' if torch.cuda.is_available() else 'cpu'
rng = np.random.default_rng(719031)
query = (rng.normal(size=(1,16,16,16)) + 1j*rng.normal(size=(1,16,16,16))) / np.sqrt(2)
config = ROOT/'src/configs/candidates/GP_MP_white_preconditioned_matched_20261104.json'
outputs, records = [], []
for cls in (Original, Organized):
    model = cls(config, device=device, batch_size=1)
    out, record = model.infer(query, 1.)
    outputs.append(out)
    records.append(record)
    del model
    gc.collect()
    if device == 'cuda':
        torch.cuda.empty_cache()
np.testing.assert_array_equal(*outputs)
assert records[0] == records[1]
report = dict(status='PASS', fixture='one seeded synthetic complex AWGN query; not a research result',
              device=device, max_absolute_difference=float(np.max(np.abs(outputs[0]-outputs[1]))),
              output_sha256=[hashlib.sha256(x.tobytes()).hexdigest() for x in outputs],
              checkpoint_sha256=records[0]['checkpoint_sha256'], training_started=False,
              formal_experiment_started=False)
(Path(__file__).parent/'CHECKPOINT_VALIDATION.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
