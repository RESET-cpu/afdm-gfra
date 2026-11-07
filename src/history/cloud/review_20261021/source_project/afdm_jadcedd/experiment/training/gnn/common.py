"""Shared physical labels, phase order, and source records for GNN training."""

from pathlib import Path
import numpy as np
import torch
from afdm_jadcedd.algorithm.baselines.gnn_aspl import (
    PAPER_SHA256,
    project_channel_coefficients,
)
from afdm_jadcedd.experiment.generate import (
    CONDITION_GENERATOR_VERSION,
    GENERATOR_VERSION,
    generate_case,
)
from afdm_jadcedd.project import ROOT
from afdm_jadcedd.utils import sha256


def grid_mode(arguments):
    # Old phase states have no field. Do not add it to their recorded recipe.
    value = getattr(arguments, "grid_mode", "off_grid")
    if value not in ("off_grid", "on_grid"):
        raise ValueError("grid_mode must be off_grid or on_grid")
    return value


def data_contract(arguments):
    on_grid = grid_mode(arguments) == "on_grid"
    return dict(
        grid_mode=grid_mode(arguments),
        generator_version=CONDITION_GENERATOR_VERSION if on_grid else GENERATOR_VERSION,
        label_scope=(
            "exact finite-dictionary physical coefficients"
            if on_grid
            else "oracle projection of continuous full-H into physical integer atoms"
        ),
        observation_scope="original physical observation, supplied complex noise variance",
        dictionary_equation_exact=on_grid,
        continuous_projection_labels=not on_grid,
        label_only_truth=True,
        inference_truth=False,
        on_grid_consistency_rtol=1e-10 if on_grid else None,
        on_grid_consistency_atol=1e-10 if on_grid else None,
    )


def case(seed, arguments):
    # Omit the keyword on the historical path, preserving its original call.
    options = {"grid_mode": "on_grid"} if grid_mode(arguments) == "on_grid" else {}
    public, truth, metadata = generate_case(
        seed,
        arguments.snr_db,
        arguments.scale,
        activity_probability=arguments.activity_probability,
        users=arguments.users,
        frames=arguments.frames,
        m_z=arguments.m_z,
        m_y=arguments.m_y,
        require_active_user=True,
        **options,
    )
    return public, truth, metadata


def coefficient_label(channel, atoms, arguments):
    label = project_channel_coefficients(channel, atoms, verify_orthogonality=False)
    if grid_mode(arguments) == "on_grid":
        h = np.asarray(channel)
        reconstructed = np.einsum(
            "kgm,grn->kmrn", label.reshape(h.shape[0], len(atoms), h.shape[1]), atoms, optimize=True
        )
        if not np.allclose(reconstructed, h, rtol=1e-10, atol=1e-10):
            raise ValueError("on_grid H is outside the declared finite physical dictionary")
    return label


def physical_row_support(truth, metadata, coordinates):
    """Occupied on-grid training rows; merge colliding physical paths."""
    if metadata.get("scene_conditions", {}).get("grid_mode") != "on_grid":
        raise ValueError("conditional slab support requires an exact on_grid physical scene")
    activity = np.asarray(truth["activity"], bool)
    support = np.zeros((len(activity), len(coordinates)), bool)
    for path in metadata["scene_conditions"]["path_parameters"]:
        if not activity[path["user_id"]]:
            continue
        match = (coordinates[:, 0] == path["folded_delay_samples"]) & (
            coordinates[:, 1] == path["doppler_hz"]
        )
        if match.sum() != 1:
            raise ValueError("occupied physical path is outside the declared integer dictionary")
        support[path["user_id"], np.flatnonzero(match)[0]] = True
    return support.reshape(-1)


def phase_schedule(layers):
    tasks = []
    for layer in range(1, layers + 1):
        tasks.extend(
            dict(layer=layer, phase=phase)
            for phase in ("gnn", "damping", "joint")
            if not (layer == 1 and phase == "gnn")
        )
        tasks.append(dict(layer=layer, phase="validation"))
    return tasks


def source_identity(trainer_path):
    """Bind new training runs to the actual package and its launch command."""
    model = ROOT / "src/afdm_jadcedd/algorithm/baselines/gnn_aspl.py"
    generator = ROOT / "src/afdm_jadcedd/experiment/generate.py"
    dictionary = ROOT / "src/afdm_jadcedd/system/dictionary.py"
    paths = [
        model,
        generator,
        ROOT / "src/afdm_jadcedd/utils.py",
        ROOT / "src/afdm_jadcedd/project.py",
        ROOT / "scripts/train_gnn.py",
        ROOT / "src/afdm_jadcedd/algorithm/baselines/ding.py",
        Path(__file__).resolve().parent.parent / "__init__.py",
    ]
    paths += sorted(Path(__file__).resolve().parent.glob("*.py"))
    paths += sorted((ROOT / "src/afdm_jadcedd/system").rglob("*.py"))
    return dict(
        paper_sha256=PAPER_SHA256,
        paper_locator="Ding pp.3-5 Eqs.(12)-(28), Sec.III-C and IV-A",
        source_report="results/baseline_revision_20261008/phase2_sources/GNN_ASPL_SOURCE.md",
        module_sha256=sha256(model),
        trainer_sha256=sha256(trainer_path),
        generator_sha256=sha256(generator),
        dictionary_sha256=sha256(dictionary),
        source_sha256={str(path.relative_to(ROOT)): sha256(path) for path in paths},
        torch_version=str(torch.__version__),
        numpy_version=str(np.__version__),
    )
