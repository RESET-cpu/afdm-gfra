"""Public-input-only receiver and frozen activity readout for off-grid SBL."""
from copy import deepcopy
from pathlib import Path
import hashlib
import json
import time
import numpy as np
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.system.observation import ReceiverInput,load_input
from afdm_jadcedd.utils import sha256,write_json
from afdm_jadcedd.algorithm.baselines.readout import nearest_node,public_snr_db
from . import sbl
from .atoms import activity_score

METHODS = {"offgrid_sbl":sbl}
DEFAULT_CONFIG = ROOT / "configs/offgrid_baselines.json"


def load_configuration(path=None):
    return json.loads((DEFAULT_CONFIG if path is None else Path(path)).read_text())


def inference_sources():
    paths = sorted(Path(__file__).parent.glob("*.py"))
    paths += sorted((ROOT/"src/afdm_jadcedd/system").rglob("*.py"))
    paths += [ROOT/"src/afdm_jadcedd/utils.py",
              ROOT/"src/afdm_jadcedd/algorithm/baselines/readout.py"]
    return {str(p.relative_to(ROOT)):sha256(p) for p in paths}


def inference_signature(config,method):
    return hashlib.sha256(json.dumps(dict(method=method,schema=config["schema"],
        solver=config["methods"][method]["solver"],sources=inference_sources()),
        sort_keys=True,separators=(",",":")).encode()).hexdigest()


class OffGridReceiver:
    def __init__(self,configuration,method):
        self.configuration = deepcopy(configuration)
        self.method = method
        if method not in METHODS or configuration.get("schema") != "afdm-offgrid-baselines-v1":
            raise ValueError("registered off-grid method and configuration required")
        self.settings = METHODS[method].Settings(**configuration["methods"][method]["solver"])
        self.signature = inference_signature(configuration,method)
        readout = configuration["readout"]
        path = ROOT/readout["path"]
        if sha256(path) != readout["sha256"]:
            raise ValueError("off-grid activity policy SHA256 mismatch")
        self.policy = json.loads(path.read_text())
        if (self.policy.get("schema") != "afdm-offgrid-activity-v1"
                or self.policy.get("statistic") != "relative_channel_frobenius_energy"
                or self.policy["methods"][method]["inference_sha256"] != self.signature):
            raise ValueError("off-grid activity policy is bound to a different inference algorithm")
        self.nodes = np.asarray(self.policy["snr_nodes_db"],float)
        self.thresholds = np.asarray(self.policy["methods"][method]["thresholds"],float)
        if (self.nodes.ndim != 1 or not len(self.nodes) or not np.isfinite(self.nodes).all()
                or np.any(np.diff(self.nodes) <= 0)
                or self.thresholds.shape != self.nodes.shape or not np.isfinite(self.thresholds).all()
                or np.any(self.thresholds < 0)):
            raise ValueError("valid frozen SNR nodes and activity thresholds required")

    def infer(self,inputs,*,observer=None):
        if not isinstance(inputs,ReceiverInput):
            raise TypeError("public four-field ReceiverInput required")
        if observer is not None:
            raise ValueError("off-grid receivers return their native traces")
        if inputs.observation.shape[-1] != 16 or inputs.operator.shape[-1] != 16:
            raise ValueError("current AFDM physical model requires N=16")
        started = time.perf_counter()
        result = METHODS[self.method].solve(inputs,self.settings)
        score,energy = activity_score(result["estimate"])
        index = nearest_node(public_snr_db(inputs),self.nodes)
        threshold = float(self.thresholds[index])
        arrays = dict(estimate=result["estimate"],component_user_ids=result["user_ids"],
            folded_delay_samples=result["positions"][:,0],
            doppler_hz=result["positions"][:,1]*30000.,component_coefficients=result["gains"],
            activity_score=score,channel_energy=energy,
            activity_decision=(score >= threshold)&(energy > 0))
        if not all(np.isfinite(value).all() for value in arrays.values()):
            raise FloatingPointError("nonfinite off-grid receiver output")
        record = {key:value for key,value in result.items()
                  if key not in ("estimate","user_ids","positions","gains")}
        record.update(status="COMPLETE",method=self.method,algorithm_id=self.method,
            seconds=time.perf_counter()-started,configuration=self.configuration,
            inference_sha256=self.signature,source_sha256=inference_sources(),
            activity_threshold=threshold,readout_snr_node_db=float(self.nodes[index]),
            activity_statistic=self.policy["statistic"],activity_comparator=">=",
            validation_status=self.configuration.get("validation_status","DEVELOPMENT"),
            component_coefficient_convention="free complex coefficient of scalar-phase-normalized AFDM atom",
            component_count_meaning="screened dictionary rows",
            supplied_noise_variance_used=True,truth_loaded=False,truth_used_in_inference=False,
            true_snr_or_activity_count_used=False,activity_count_or_truth_used=False,
            continuous_delay_doppler_estimation=True,paper_implementation_scope="AFDM/MMV adaptation")
        return arrays,record

    def run(self,input_path,output_path,*,observer=None):
        output = Path(output_path)
        if output.suffix != ".npz" or output.exists() or output.with_suffix(".json").exists():
            raise ValueError("fresh .npz output required")
        arrays,record = self.infer(load_input(input_path),observer=observer)
        output.parent.mkdir(parents=True,exist_ok=True)
        np.savez_compressed(output,**arrays)
        record.update(input_sha256=sha256(input_path),output_sha256=sha256(output))
        write_json(output.with_suffix(".json"),record)
        return record
