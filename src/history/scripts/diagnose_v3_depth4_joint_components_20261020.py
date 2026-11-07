"""Fixed-weight CPU component replacements between two adjacent joint checkpoints."""
from diagnose_v3_v2_depth4_q8_20261020 import ROOT, PREVIOUS, OUT, read, write, sha, physical
import copy
import importlib
import itertools
import os
from pathlib import Path
import shutil
import sys
import time
import numpy as np


def main():
    extension = "--raw-score" in sys.argv
    folder = OUT/("joint_raw_score_replay" if extension else "joint_component_replay")
    if folder.exists():
        raise FileExistsError(folder)
    prior = read(OUT/"training_stages/PLAN.json")
    for path, digest in prior["checkpoints"].items():
        assert sha(path) == digest
    plan = read(PREVIOUS/"PLAN.json")
    bound = plan["models"]["v3"]
    case = prior["case"]
    folder.mkdir()
    shutil.copy2(__file__, folder/Path(__file__).name)
    write(folder/"PLAN.json", dict(
        parent_stage_plan_sha256=sha(OUT/"training_stages/PLAN.json"),
        source_sha256=sha(folder/Path(__file__).name), case=case, checkpoints=prior["checkpoints"],
        interventions=("Separate score network weights from alpha; locate the affected layer."
                       if extension else
                       "All 2x2x2 combinations of score+alpha, activity, gamma+beta from epochs 2 and 3. "
                       "Also replace these groups only in layer 1 of epoch 3."),
        post_hoc_diagnosis=True, new_weights_trained=False, checkpoint_selection_changed=False,
        gpu_used=False))
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
    models = {}
    for epoch in (2, 3):
        saved = torch.load(Path(bound["run"])/"checkpoints/depth_4"/f"epoch_{epoch}.pt",
                           map_location="cpu", weights_only=False, mmap=True)
        model = receiver.Receiver()
        for _ in range(4):
            model.add_layer(None)
        model.load_state_dict(saved["state"], strict=True)
        model.eval()
        model.use_checkpoint = False
        models[epoch] = model
        del saved
    with np.load(Path(case["folder"])/"input.npz") as f:
        public, _ = data.prepare_public(
            dict(y=f["observation"], a=f["operator"], noise=f["noise_variance"], rho=f["activity_prior"]),
            plan["scale"], "cpu", phase_mode="known", noise_mode="known")
    with np.load(Path(case["folder"])/"truth.npz") as f:
        truth, active = f["channel"].copy(), f["activity"].astype(bool)

    def evaluate(model):
        outputs, _ = model(public)
        final = outputs[-1]
        p = torch.sigmoid(final["logits"]).numpy()
        pred = physical(final["estimate"], plan["scale"])
        conditional = physical(final["conditional"], plan["scale"])
        return dict(nmse_db=float(10*np.log10((abs(pred-truth)**2).sum()/(abs(truth)**2).sum())),
                    target_probability=float(p[27]),
                    target_conditional_error=float((abs(conditional[27]-truth[27])**2).sum()),
                    misses=int((active & (p < .5)).sum()), false_alarms=int((~active & (p >= .5)).sum()),
                    layer_target_probabilities=[float(torch.sigmoid(x["logits"])[27]) for x in outputs])

    results = []
    with torch.no_grad():
        for s, a, m in ([] if extension else itertools.product((2, 3), repeat=3)):
            hybrid = copy.deepcopy(models[3])
            for i, layer in enumerate(hybrid.layers):
                layer.score = models[s].layers[i].score
                layer.c_alpha = models[s].layers[i].c_alpha
                layer.activity = models[a].layers[i].activity
                layer.c_gamma = models[m].layers[i].c_gamma
                layer.c_beta = models[m].layers[i].c_beta
            row = dict(variant=f"score_epoch{s}_activity_epoch{a}_messages_epoch{m}", **evaluate(hybrid))
            if s == a == m:
                baseline = next(v for v in read(OUT/"training_stages/RESULTS.json") if v["epoch"] == s)["trace"][-1]
                assert abs(row["nmse_db"]-baseline["nmse_db"]) < 1e-12
                assert row["target_probability"] == baseline["target_probability"]
            results.append(row)
            print(row["variant"], row["nmse_db"], row["target_probability"], row["misses"], flush=True)
            del hybrid
        for group in ([] if extension else ("score", "activity", "messages", "score_and_activity")):
            hybrid = copy.deepcopy(models[3])
            layer, reference = hybrid.layers[0], models[2].layers[0]
            if group in ("score", "score_and_activity"):
                layer.score, layer.c_alpha = reference.score, reference.c_alpha
            if group in ("activity", "score_and_activity"):
                layer.activity = reference.activity
            if group == "messages":
                layer.c_gamma, layer.c_beta = reference.c_gamma, reference.c_beta
            row = dict(variant="first_layer_epoch2_"+group, **evaluate(hybrid))
            results.append(row)
            print(row["variant"], row["nmse_db"], row["target_probability"], row["misses"], flush=True)
            del hybrid
        if extension:
            variants = [
                ("raw_score_all_layers", range(4), True, False),
                ("alpha_all_layers", range(4), False, True),
                ("score_and_alpha_layer2", [1], True, True),
                ("score_and_alpha_layer3", [2], True, True),
                ("score_and_alpha_layer4", [3], True, True),
                ("score_and_alpha_layers1_2", [0, 1], True, True)]
            for label, indices, replace_score, replace_alpha in variants:
                hybrid = copy.deepcopy(models[3])
                for i in indices:
                    if replace_score:
                        hybrid.layers[i].score = models[2].layers[i].score
                    if replace_alpha:
                        hybrid.layers[i].c_alpha = models[2].layers[i].c_alpha
                row = dict(variant="epoch2_"+label, **evaluate(hybrid))
                results.append(row)
                print(row["variant"], row["nmse_db"], row["target_probability"], row["misses"], flush=True)
                del hybrid
    for path, digest in prior["checkpoints"].items():
        assert sha(path) == digest
    write(folder/"RESULTS.json", results)
    write(folder/"AUDIT.json", dict(status="PASSED", gpu_used=False, checkpoints_unchanged=True,
                                   same_stage_baseline_parity_verified=not extension,
                                   parent_baseline_parity_audit=(str(OUT/"joint_component_replay/AUDIT.json")
                                                                if extension else None)))
    write(folder/"COMPLETE.json", dict(status="COMPLETE", completed_unix=time.time(),
                                      results_sha256=sha(folder/"RESULTS.json")))


if __name__ == "__main__":
    main()
