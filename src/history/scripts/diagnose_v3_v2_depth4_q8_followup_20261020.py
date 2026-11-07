"""Follow up the first-feedback-mean finding; CPU, one revealed scene, fixed weights."""
from diagnose_v3_v2_depth4_q8_20261020 import (
    ROOT, PREVIOUS, OUT, read, write, sha, physical)
import copy
import importlib
import os
from pathlib import Path
import shutil
import sys
import time
import traceback
import numpy as np

FOLLOW = OUT / "first_layer_followup"


def main():
    if FOLLOW.exists():
        raise FileExistsError(FOLLOW)
    assert read(OUT / "AUDIT.json")["status"] == "PASSED"
    FOLLOW.mkdir()
    shutil.copy2(__file__, FOLLOW / Path(__file__).name)
    (FOLLOW / "RUNNING.lock").write_text(str(os.getpid()), encoding="ascii")
    try:
        run()
    except BaseException as error:
        write(FOLLOW / f"FAILURE_{time.time_ns()}.json",
              dict(error=repr(error), traceback=traceback.format_exc()))
        raise
    finally:
        (FOLLOW / "RUNNING.lock").unlink(missing_ok=True)


def run():
    plan = read(PREVIOUS / "PLAN.json")
    bound = plan["models"]
    source_plan = read(OUT / "PLAN.json")
    for path, digest in source_plan["frozen_hashes"].items():
        assert sha(path) == digest
    scale = plan["scale"]
    case = next(c for c in plan["cases"] if c["group"] == "k40_q8" and c["index"] == 5)
    write(FOLLOW / "PLAN.json", dict(
        parent_audit_sha256=sha(OUT / "AUDIT.json"), parent_plan_sha256=sha(OUT / "PLAN.json"),
        source_sha256=sha(FOLLOW / Path(__file__).name), target_case=case,
        purpose="Locate the first feedback mean difference already observed to restore detection.",
        interventions=[
            "Replace matched score, alpha and activity together at one layer or early prefix.",
            "Replace first-layer posterior probabilities and/or conditional means by saved old outputs; "
            "hold the new query, feedback ratio and outgoing scalar variance fixed.",
            "Replace the first outgoing mean only at selected true-active users, or inactive users. "
            "These truth-selected subsets are post-hoc oracle localization, not receiver modifications."],
        learned_weights_updated=False, gpu_used=False, post_hoc=True))
    os.environ["AFDM_LSTMP_ROOT"] = str(ROOT)
    os.environ["AFDM_LSTMP_CONFIG"] = bound["v3"]["config"]
    sys.path.insert(0, str(Path(bound["v3"]["run"]) / "source_code"))
    import torch
    import psutil
    from threadpoolctl import threadpool_limits
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    threadpool_limits(2)
    from experiments.lstmp_candidate_20261019 import common, data
    from experiments.lstmp_candidate_20261019.message_damping import damp_gaussian
    receiver = importlib.import_module("experiments.lstmp_execution_v3_20261020.receiver")
    models = {}
    for name, b in bound.items():
        checkpoint = torch.load(b["checkpoint"], map_location="cpu", weights_only=False, mmap=True)
        model = receiver.Receiver()
        for _ in range(4):
            model.add_layer(None)
        model.load_state_dict(checkpoint["state"], strict=True)
        model.eval()
        model.use_checkpoint = False
        models[name] = model
        del checkpoint
    with np.load(Path(case["folder"]) / "input.npz") as f:
        public, _ = data.prepare_public(
            dict(y=f["observation"], a=f["operator"], noise=f["noise_variance"], rho=f["activity_prior"]),
            scale, "cpu", phase_mode="known", noise_mode="known")
    with np.load(Path(case["folder"]) / "truth.npz") as f:
        truth, active = f["channel"].copy(), f["activity"].astype(bool)

    def forward(model, patch=None):
        y, a, rho = public["y"], public["a"], public["rho"]
        prior = y.new_zeros(public["channel_shape"])
        reference = y.new_tensor(rho * common.CONFIG["normalized_training_second_moment"])
        variance = reference
        first = None
        trajectory = []
        for i, layer in enumerate(model.layers):
            r, v, _ = receiver.base.linear_query(public, prior, variance, layer.c_gamma)
            mu = r + torch.exp(layer.c_alpha)*v/2 * model.score_call(layer.score, r, v.expand(len(r)))
            p = torch.sigmoid(layer.activity(r, v.expand(len(r)), mu, rho))
            estimate = p[:, None, None, None, None]*mu
            residual = y - a @ data.pack(estimate)
            frames, columns = y.shape[0]//2, y.shape[1]
            raw = (residual.square().sum()-frames*columns*public["noise"]) / (columns*a.square().sum()/2)
            post, ratio = receiver.base.feedback_variance(raw, v, layer.c_beta, order="after_positive")
            next_prior, next_v, amount = damp_gaussian(
                prior, variance, (estimate-ratio*r)/(1-ratio), post/(1-ratio), reference)
            if i == 0:
                assert float(amount) == 1.
                first = dict(query=r, conditional=mu, probabilities=p, prior=next_prior,
                             variance=next_v, ratio=ratio)
                if patch:
                    next_prior = patch(first)
                    assert next_prior.shape == prior.shape
            trajectory.append(dict(layer=i+1, probability_user27=float(p[27]),
                                   conditional_user27_error=float((abs(physical(mu, scale)[27]-truth[27])**2).sum())))
            prior, variance = next_prior, next_v
        pred = physical(estimate, scale)
        error = (abs(pred-truth)**2).reshape(len(truth), -1).sum(1)
        probability = p.numpy()
        row = dict(nmse_db=float(10*np.log10(error.sum()/(abs(truth)**2).sum())),
                   misses=int((active & (probability < .5)).sum()),
                   false_alarms=int((~active & (probability >= .5)).sum()),
                   probability_user27=float(probability[27]),
                   conditional_user27_error=trajectory[-1]["conditional_user27_error"],
                   trajectory=trajectory)
        return row, first, pred, probability

    results = []
    with torch.no_grad():
        first = {}
        for name, model in models.items():
            row, state, pred, probability = forward(model)
            with np.load(PREVIOUS/name/"k40_q8/005.npz") as f:
                assert np.array_equal(pred, f["estimate"])
                assert np.array_equal(probability, f["probabilities"])
            first[name] = state
            results.append(dict(variant="baseline_"+name, **row))
        for indices in ([0], [1], [2], [3], [0, 1], [0, 1, 2]):
            hybrid = copy.deepcopy(models["v3"])
            for i in indices:
                hybrid.layers[i].score = models["v2"].layers[i].score
                hybrid.layers[i].activity = models["v2"].layers[i].activity
                hybrid.layers[i].c_alpha = models["v2"].layers[i].c_alpha
            row, _, _, _ = forward(hybrid)
            key = "old_matched_networks_layers_" + "_".join(str(i+1) for i in indices)
            results.append(dict(variant=key, **row))
            print(key, row["nmse_db"], row["probability_user27"], flush=True)
            del hybrid
        for components in (("probabilities",), ("conditional",), ("probabilities", "conditional")):
            def patch(state, components=components):
                p = first["v2"]["probabilities"] if "probabilities" in components else state["probabilities"]
                mu = first["v2"]["conditional"] if "conditional" in components else state["conditional"]
                return (p[:, None, None, None, None]*mu-state["ratio"]*state["query"])/(1-state["ratio"])
            row, _, _, _ = forward(models["v3"], patch)
            key = "first_mean_old_" + "_".join(components) + "_new_scalar_variance"
            results.append(dict(variant=key, **row))
            print(key, row["nmse_db"], row["probability_user27"], flush=True)
        for indices in ([22], [27], [31], [35], [37], [22, 31], np.flatnonzero(active).tolist(),
                        np.flatnonzero(~active).tolist()):
            def patch(state, indices=indices):
                mean = state["prior"].clone()
                mean[indices] = first["v2"]["prior"][indices]
                return mean
            row, _, _, _ = forward(models["v3"], patch)
            key = "first_old_mean_users_" + "_".join(map(str, indices))
            results.append(dict(variant=key, oracle_subset_selection=True, user_indices_zero_based=indices, **row))
            print(key, row["nmse_db"], row["probability_user27"], flush=True)
    for path, digest in source_plan["frozen_hashes"].items():
        assert sha(path) == digest
    write(FOLLOW / "RESULTS.json", results)
    write(FOLLOW / "AUDIT.json", dict(status="PASSED", baseline_parity_max_abs=0.,
                                     frozen_assets_verified=True, gpu_used=False, weight_updates=False))
    write(FOLLOW / "COMPLETE.json", dict(status="COMPLETE", completed_unix=time.time(),
                                        result_sha256=sha(FOLLOW / "RESULTS.json"),
                                        audit_sha256=sha(FOLLOW / "AUDIT.json")))


if __name__ == "__main__":
    main()
