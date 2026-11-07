"""Read-only CPU replay of the revealed failing case at saved training stages."""
from diagnose_v3_v2_depth4_q8_20261020 import (
    ROOT, PREVIOUS, OUT, read, write, sha, physical)
import importlib
import os
from pathlib import Path
import shutil
import sys
import time
import numpy as np


def main():
    folder = OUT / "training_stages"
    if folder.exists():
        raise FileExistsError(folder)
    plan = read(PREVIOUS / "PLAN.json")
    bound = plan["models"]["v3"]
    case = next(c for c in plan["cases"] if c["group"] == "k40_q8" and c["index"] == 5)
    paths = {e: Path(bound["run"])/"checkpoints/depth_4"/f"epoch_{e}.pt" for e in (1, 2, 3)}
    hashes = {str(p): sha(p) for p in paths.values()}
    for f, h in case["files"].items():
        assert sha(Path(case["folder"])/f) == h
    assert sha(paths[3]) == sha(bound["checkpoint"])
    folder.mkdir()
    shutil.copy2(__file__, folder/Path(__file__).name)
    write(folder/"PLAN.json", dict(case=case, checkpoints=hashes, selection_changed=False,
                                  post_hoc_diagnosis=True, gpu_used=False,
                                  source_sha256=sha(folder/Path(__file__).name)))
    os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
    os.environ["AFDM_LSTMP_CONFIG"] = bound["config"]
    sys.path.insert(0, str(Path(bound["run"])/"source_code"))
    import torch
    import psutil
    from threadpoolctl import threadpool_limits
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    threadpool_limits(2)
    from experiments.lstmp_candidate_20261019 import data
    receiver = importlib.import_module("experiments.lstmp_execution_v3_20261020.receiver")
    with np.load(Path(case["folder"])/"input.npz") as f:
        public, _ = data.prepare_public(
            dict(y=f["observation"], a=f["operator"], noise=f["noise_variance"], rho=f["activity_prior"]),
            plan["scale"], "cpu", phase_mode="known", noise_mode="known")
    with np.load(Path(case["folder"])/"truth.npz") as f:
        truth, active = f["channel"].copy(), f["activity"].astype(bool)
    result = []
    with torch.no_grad():
        for epoch, path in paths.items():
            saved = torch.load(path, map_location="cpu", weights_only=False, mmap=True)
            assert saved["epoch"] == epoch and saved["depth"] == 4
            model = receiver.Receiver()
            for _ in range(4):
                model.add_layer(None)
            model.load_state_dict(saved["state"], strict=True)
            model.eval()
            model.use_checkpoint = False
            outputs, diagnostics = model(public)
            rows = []
            for i, last in enumerate(outputs):
                pred = physical(last["estimate"], plan["scale"])
                conditional = physical(last["conditional"], plan["scale"])
                p = torch.sigmoid(last["logits"]).numpy()
                err = (abs(pred-truth)**2).reshape(len(truth), -1).sum(1)
                ce = (abs(conditional-truth)**2).reshape(len(truth), -1).sum(1)
                rows.append(dict(
                    layer=i+1, nmse_db=float(10*np.log10(err.sum()/(abs(truth)**2).sum())),
                    misses=int((active & (p < .5)).sum()), false_alarms=int((~active & (p >= .5)).sum()),
                    target_probability=float(p[27]), target_conditional_error=float(ce[27]),
                    probabilities=p.tolist(), conditional_user_errors=ce.tolist(),
                    effective_user_errors=err.tolist(), diagnostics=diagnostics[i]))
            if epoch == 3:
                with np.load(PREVIOUS/"v3/k40_q8/005.npz") as old:
                    assert np.array_equal(pred, old["estimate"])
                    assert np.array_equal(p, old["probabilities"])
            result.append(dict(epoch=epoch, trace=rows))
            print(epoch, rows[-1]["nmse_db"], rows[-1]["target_probability"], rows[-1]["misses"], flush=True)
            del model, saved, outputs
    for p, h in hashes.items():
        assert sha(p) == h
    write(folder/"RESULTS.json", result)
    write(folder/"AUDIT.json", dict(status="PASSED", checkpoint_hashes_verified=True,
                                   epoch3_baseline_parity_max_abs=0., gpu_used=False, weights_updated=False))
    write(folder/"COMPLETE.json", dict(status="COMPLETE", completed_unix=time.time(),
                                      result_sha256=sha(folder/"RESULTS.json")))


if __name__ == "__main__":
    main()
