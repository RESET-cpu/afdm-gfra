"""Frozen score pair, activity classifier and current receiver configuration."""

import json
from pathlib import Path

from project import ROOT, CONFIGS
from utils import sha256

METHOD = "full_score"
EVIDENCE_MODES = ("classifier",)
DEFAULT_CONFIG = CONFIGS / "final/STMP.json"


def load_configuration(path=None):
    return json.loads((DEFAULT_CONFIG if path is None else Path(path)).read_text())


def verify(configuration=None):
    """Check the saved teacher/prior bindings without making network queries."""
    import torch
    from .records import SpatialConfig
    from .activity import SCHEMA, FEATURE_DEFINITION_FROZEN

    c = load_configuration() if configuration is None else configuration
    if c["implementation"] != METHOD or c["activity_evidence"] not in EVIDENCE_MODES:
        raise ValueError("Full-channel score and a registered activity evidence required")
    if c.get("conditional_mean_projection", "none") not in ("none", "rank_one"):
        raise ValueError("conditional_mean_projection must be none or rank_one")
    controls = SpatialConfig(**c["ep"])
    controls.validate_stopping()
    if (
        controls.covariance_mode != "isotropic"
        or c["site_damping"] != 1.0
        or c["decision_threshold"] != 0.5
        or c["scale"] <= 0
        or c["conditional_variance_floor_checkpoint_normalized"] <= 0
        or c["initialization"]["kind"] != "activity_prior_times_training_power"
    ):
        raise ValueError("Frozen isotropic message and initialization policy required")
    prior_path = ROOT / c["prior_definition"]
    if sha256(prior_path) != c["prior_definition_sha256"]:
        raise ValueError("Training prior definition changed")
    prior = json.loads(prior_path.read_text())
    hashes = {}
    blobs = {}
    keys = ["first_checkpoint", "second_checkpoint"]
    if c["activity_evidence"] == "classifier":
        keys.append("evidence_checkpoint")
    for key in keys:
        path = ROOT / c[key]
        digest = sha256(path)
        if digest != c[key + "_sha256"]:
            raise ValueError("Frozen checkpoint changed: " + key)
        hashes[key] = digest
        blobs[key] = torch.load(path, map_location="cpu", weights_only=False)
    first, second = blobs["first_checkpoint"], blobs["second_checkpoint"]
    if (
        first.get("schema") != "afdm-cai-direct-score-v1"
        or first["order"] != 1
        or second.get("schema") != "afdm-cai-direct-score-v1"
        or second["order"] != 2
        or second["metadata"]["objective"] != "direct_cai_global_trace"
        or second["metadata"]["first_sha256"] != hashes["first_checkpoint"]
        or first["global_complex_rms"] != second["global_complex_rms"]
        or c["scale"] != first["global_complex_rms"]
        or prior["global_complex_rms"] != c["scale"]
    ):
        raise ValueError("Same frozen teacher and training coordinates required")
    if "evidence_checkpoint" in blobs:
        evidence = blobs["evidence_checkpoint"]
        if (
            evidence.get("schema") != SCHEMA
            or evidence["training_class_prior"] != 0.5
            or evidence.get("feature_definition") != FEATURE_DEFINITION_FROZEN
            or evidence["first_sha256"] != hashes["first_checkpoint"]
            or evidence["second_sha256"] != hashes["second_checkpoint"]
            or evidence["metadata"]["prior_definition_sha256"] != c["prior_definition_sha256"]
            or evidence["prior_definition"] != prior
            or evidence["scale"] != c["scale"]
        ):
            raise ValueError("Same-prior complete-input classifier required")
    return dict(
        status="PASS",
        method=METHOD,
        activity_evidence=c["activity_evidence"],
        checkpoint_sha256=hashes,
        network_queries=0,
    )
