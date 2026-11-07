#!/usr/bin/env python3
"""Layerwise Ding GNN-ASPL training; --smoke is a bounded execution check.

Entry: training.gnn.cli.main, using the per-snr recipe.
         --output NEW_GNN_SMOKE
Full mode generates >10,000 independent training samples at one specified SNR.
--preliminary uses a declared smaller training budget (default 512+64 cases)
while retaining all 29 phases, ten AMP layers and effective batch size 128.
--grid-mode on_grid uses exact finite-dictionary physical coefficient labels;
the historical off_grid default retains continuous projected labels.
Each completed training phase and layer validation saves training_state.pt.
Resume with --resume OUTPUT/training_state.pt; no recipe arguments are needed.
An interrupted phase is rerun from its last completed boundary.
"""
from dataclasses import asdict
from collections import OrderedDict
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time


import numpy as np
import torch

from receiver.baseline.gnn import CHECKPOINT_SCHEMA
from receiver.baseline.gnn import INTEGER_GRID
from receiver.baseline.gnn import METHOD
from receiver.baseline.gnn import GNNASPLNetwork
from receiver.baseline.gnn import GNNASPLSettings
from receiver.baseline.gnn import coefficient_nmse
from receiver.baseline.gnn import project_channel_coefficients
from channel.dictionary import AFDMGrid
from channel.dictionary import physical_atoms
from fileio import sha256
from fileio import state_sha
from fileio import write_json


from training.gnn.common import grid_mode
from training.gnn.common import data_contract
from training.gnn.common import case
from training.gnn.common import coefficient_label
from training.gnn.common import physical_row_support
from training.gnn.common import phase_schedule
from training.gnn.common import source_identity as training_source_identity


TRAINING_STATE_SCHEMA = "ding-gnn-aspl-training-state-v1"


def parser():
    p = argparse.ArgumentParser(prog="train_gnn.py per-snr", description=__doc__)
    p.add_argument("--output", type=Path)
    p.add_argument("--snr-db", type=float)
    p.add_argument(
        "--resume", type=Path, help="restore an existing phase-boundary training_state.pt"
    )
    p.add_argument(
        "--stop-after-phase",
        type=int,
        help="bounded development check: stop after this absolute training-phase count",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument(
        "--smoke",
        action="store_true",
        help="2 training / 1 validation cases; small public dimensions",
    )
    mode.add_argument(
        "--preliminary",
        action="store_true",
        help="real training with a declared smaller-than-paper sample budget",
    )
    p.add_argument("--train-samples", type=int)
    p.add_argument("--validation-samples", type=int)
    p.add_argument("--batch-size", type=int, default=128)
    p.add_argument(
        "--microbatch-size",
        type=int,
        default=1,
        help="gradient accumulation retains the declared effective batch size",
    )
    p.add_argument("--gnn-epochs", type=int, default=1)
    p.add_argument("--damping-epochs", type=int, default=1)
    p.add_argument("--joint-epochs", type=int, default=1)
    p.add_argument("--learning-rate", type=float, default=5e-3)
    p.add_argument("--train-seed-base", type=int, default=81000000)
    p.add_argument("--validation-seed-base", type=int, default=91000000)
    p.add_argument("--model-seed", type=int, default=61008)
    p.add_argument("--users", type=int, default=40)
    p.add_argument("--frames", type=int, default=16)
    p.add_argument("--m-z", type=int, default=4)
    p.add_argument("--m-y", type=int, default=4)
    p.add_argument("--activity-probability", type=float, default=0.1)
    p.add_argument(
        "--grid-mode",
        choices=("off_grid", "on_grid"),
        default="off_grid",
        help="physical scene grid; on_grid labels exactly represent H in the declared dictionary",
    )
    p.add_argument("--scale", type=float, default=1.0)
    p.add_argument("--threads", type=int, default=2)
    p.add_argument(
        "--tensor-cache-mib",
        type=int,
        help="bounded RAM cache of deterministic training/validation tensors; default preliminary=4096, other=0",
    )
    return p


class DeterministicTensorCache:
    """Bounded in-process LRU; it changes no generated inputs or label statistics."""

    def __init__(self, limit_mib=0):
        if not isinstance(limit_mib, int) or limit_mib < 0:
            raise ValueError("nonnegative integer tensor cache size required")
        self.limit_bytes = limit_mib * 2**20
        self.rows = OrderedDict()
        self.bytes = self.peak_bytes = self.hits = self.misses = self.evictions = 0

    def row(self, seed, arguments, atoms):
        key = (
            seed,
            arguments.snr_db,
            arguments.scale,
            arguments.users,
            arguments.frames,
            arguments.m_z,
            arguments.m_y,
            arguments.activity_probability,
            grid_mode(arguments),
        )
        if key in self.rows:
            self.hits += 1
            self.rows.move_to_end(key)
            return self.rows[key]
        self.misses += 1
        row = training_row(seed, arguments, atoms)
        size = sum(value.nbytes for value in row.values() if isinstance(value, np.ndarray))
        if size <= self.limit_bytes:
            while self.rows and self.bytes + size > self.limit_bytes:
                _, removed = self.rows.popitem(last=False)
                self.bytes -= sum(
                    value.nbytes for value in removed.values() if isinstance(value, np.ndarray)
                )
                self.evictions += 1
            self.rows[key] = row
            self.bytes += size
            self.peak_bytes = max(self.peak_bytes, self.bytes)
        return row

    def statistics(self):
        return dict(
            kind="bounded deterministic RAM tensors",
            limit_bytes=self.limit_bytes,
            stored_tensor_bytes=self.bytes,
            peak_tensor_bytes=self.peak_bytes,
            entries=len(self.rows),
            hits=self.hits,
            misses=self.misses,
            evictions=self.evictions,
            disk_data_cache_used=False,
        )


def label_statistics(label, truth, metadata, arguments, atoms):
    activity = np.asarray(truth["activity"], bool)
    active = label.reshape(arguments.users, len(atoms), -1)[activity]
    statistics = dict(active_energy=float(np.sum(abs(active) ** 2)),
                      active_coordinates=active.size, active_users=int(activity.sum()))
    if grid_mode(arguments) == "on_grid":
        _, coordinates, _ = physical_atoms(**INTEGER_GRID)
        support = physical_row_support(truth, metadata, coordinates)
        if np.max(abs(label[~support]), initial=0.0) > 1e-10 * max(1.0, np.max(abs(label))):
            raise ValueError("on_grid projection has signal outside its physical path support")
        occupied = label[support]
        statistics.update(slab_energy=float(np.sum(abs(occupied) ** 2)),
                          slab_coordinates=occupied.size, active_rows=int(support.sum()))
    return statistics


def training_row(seed, arguments, atoms):
    public, truth, metadata = case(seed, arguments)
    grid = AFDMGrid.from_operator(public["operator"], **INTEGER_GRID)
    # Accumulate gamma from the original complex128 projection, before the
    # complex64 training cast. Caching must not alter that fitted scalar.
    label = coefficient_label(truth["channel"], atoms, arguments)
    physical_design = grid.design * grid.norms[None, :]
    if grid_mode(arguments) == "on_grid":
        clean = np.einsum("qkn,kmrn->qmr", public["operator"], truth["channel"], optimize=False)
        if not np.allclose(physical_design @ label, grid.stack(clean), rtol=1e-10, atol=1e-10):
            raise ValueError("on_grid observation and physical coefficient label are inconsistent")
    return dict(
        design=np.asarray(physical_design, np.complex64),
        observation=np.asarray(grid.stack(public["observation"]), np.complex64),
        target=np.asarray(label, np.complex64),
        noise=np.asarray(public["noise_variance"], np.float32),
        **label_statistics(label, truth, metadata, arguments, atoms),
    )


def fit_gamma(arguments, seeds, atoms, cache=None):
    """Fit the conditional on-grid slab, or the historical off-grid projection proxy."""
    energy, coordinates, active_users = 0.0, 0, 0
    occupied_rows = 0
    on_grid = grid_mode(arguments) == "on_grid"
    for seed in seeds:
        if cache is not None and cache.limit_bytes:
            row = cache.row(seed, arguments, atoms)
        else:
            _, truth, metadata = case(seed, arguments)
            z = coefficient_label(truth["channel"], atoms, arguments)
            row = label_statistics(z, truth, metadata, arguments, atoms)
        energy += row["slab_energy" if on_grid else "active_energy"]
        coordinates += row["slab_coordinates" if on_grid else "active_coordinates"]
        active_users += row["active_users"]
        occupied_rows += row.get("active_rows", 0)
    gamma = energy / coordinates if coordinates else 0.0
    if not np.isfinite(gamma) or gamma <= 0:
        raise ValueError("positive slab variance requires nonempty finite training labels")
    label_scope = (
        "training only; exact finite-dictionary on-grid physical coefficients"
        if grid_mode(arguments) == "on_grid"
        else "training only; oracle integer-atom projection of full-H"
    )
    result = dict(
        physical_variance=gamma,
        label_scope=label_scope,
        conditioning=("lambda_n=1; physical occupied rows with collisions merged" if on_grid
                      else "active users only; includes all grid/antenna coordinates in their blocks"),
        pooling="scalar shared across users, grid nodes and antennas",
        coordinate_count=coordinates,
        active_user_count=active_users,
        fitted_energy=energy,
        frozen_during_training_and_inference=True,
        calibration_or_test_truth_used=False,
    )
    if on_grid:
        result.update(occupied_row_count=occupied_rows,
                      support_definition="declared on-grid path coordinates; no magnitude threshold",
                      estimator="sum |Z_nm|^2 / occupied row-antenna coordinate count")
    return result


def load_batch(arguments, seeds, atoms, cache=None):
    designs, observations, targets, noises = [], [], [], []
    for seed in seeds:
        row = (
            training_row(seed, arguments, atoms)
            if cache is None
            else cache.row(seed, arguments, atoms)
        )
        designs.append(row["design"])
        observations.append(row["observation"])
        targets.append(row["target"])
        noises.append(row["noise"])
    return (
        torch.as_tensor(np.stack(designs)),
        torch.as_tensor(np.stack(observations)),
        torch.as_tensor(np.stack(noises), dtype=torch.float32),
        torch.as_tensor(np.stack(targets)),
    )


def validate(model, arguments, seeds, atoms, layers, cache=None):
    model.eval()
    loss_sum = 0.0
    with torch.no_grad():
        for offset in range(0, len(seeds), arguments.microbatch_size):
            selected = seeds[offset : offset + arguments.microbatch_size]
            design, y, noise, target = load_batch(arguments, selected, atoms, cache)
            result = model(design, y, noise, arguments.users, layers=layers)
            loss_sum += len(selected) * float(coefficient_nmse(result["mean"], target))
    model.train()
    return loss_sum / len(seeds)


def train_phase(model, arguments, seeds, atoms, layers, phase, epochs, cache=None):
    parameters = model.phase_parameters(layers, phase)
    if not parameters:
        return []  # Stage 1 has no preceding GNN.
    optimizer = torch.optim.Adam(parameters, lr=arguments.learning_rate)
    records = []
    for epoch in range(epochs):
        rng = np.random.default_rng(
            np.random.SeedSequence(
                [arguments.model_seed, layers, {"gnn": 0, "damping": 1, "joint": 2}[phase], epoch]
            )
        )
        shuffled = np.asarray(seeds)[rng.permutation(len(seeds))].tolist()
        epoch_loss, optimizer_steps = 0.0, 0
        for offset in range(0, len(shuffled), arguments.batch_size):
            batch = shuffled[offset : offset + arguments.batch_size]
            optimizer.zero_grad(set_to_none=True)
            for micro_offset in range(0, len(batch), arguments.microbatch_size):
                selected = batch[micro_offset : micro_offset + arguments.microbatch_size]
                design, y, noise, target = load_batch(arguments, selected, atoms, cache)
                result = model(design, y, noise, arguments.users, layers=layers)
                loss = coefficient_nmse(result["mean"], target)
                if not torch.isfinite(loss):
                    raise FloatingPointError("nonfinite training loss")
                (loss * (len(selected) / len(batch))).backward()
                epoch_loss += len(selected) * float(loss.detach())
            if not all(p.grad is None or torch.isfinite(p.grad).all() for p in parameters):
                raise FloatingPointError("nonfinite GNN-ASPL training gradient")
            optimizer.step()
            optimizer_steps += 1
        records.append(
            dict(
                layer=layers,
                phase=phase,
                epoch=epoch + 1,
                coefficient_nmse=epoch_loss / len(seeds),
                optimizer_steps=optimizer_steps,
            )
        )
    return records


def source_identity():
    return training_source_identity(__file__)


def recipe_identity(arguments):
    # Output/resume/stop locations control execution, not the training recipe.
    recipe = {
        key: value
        for key, value in vars(arguments).items()
        if key not in ("output", "resume", "stop_after_phase", "tensor_cache_mib")
    }
    recipe.update(
        architecture=asdict(GNNASPLSettings()),
        dictionary=INTEGER_GRID,
        optimizer="Adam",
        optimizer_reset_each_phase=True,
    )
    encoded = json.dumps(recipe, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    return recipe, hashlib.sha256(encoded).hexdigest()


def resolve_arguments(argv):
    command_parser = parser()
    tokens = sys.argv[1:] if argv is None else list(argv)
    arguments = command_parser.parse_args(tokens)
    resumed = None
    if arguments.resume is not None:
        resumed = torch.load(arguments.resume, map_location="cpu", weights_only=True)
        if resumed.get("schema") != TRAINING_STATE_SCHEMA or resumed.get("method") != METHOD:
            raise ValueError("a GNN-ASPL training-state checkpoint is required for resume")
        saved = resumed["arguments"]
        mentioned = {token.split("=", 1)[0] for token in tokens}
        explicit = {
            action.dest
            for action in command_parser._actions
            if any(option in mentioned for option in action.option_strings)
        }
        for key in explicit - {"resume", "stop_after_phase", "help", "tensor_cache_mib"}:
            value = getattr(arguments, key)
            recorded = saved.get(key, "off_grid") if key == "grid_mode" else saved[key]
            same = (
                (Path(value).resolve() == Path(recorded).resolve())
                if key == "output"
                else value == recorded
            )
            if not same:
                raise ValueError(f"resume cannot change recorded training argument {key}")
        cache_override = (
            arguments.tensor_cache_mib
            if "tensor_cache_mib" in explicit
            else saved["tensor_cache_mib"]
        )
        arguments = argparse.Namespace(
            **saved, resume=arguments.resume, stop_after_phase=arguments.stop_after_phase
        )
        arguments.tensor_cache_mib = cache_override
        arguments.output = Path(arguments.output)
    else:
        if arguments.output is None or arguments.snr_db is None:
            raise ValueError("--output and --snr-db are required for a new training run")
        if arguments.smoke:
            arguments.train_samples, arguments.validation_samples = 2, 1
            arguments.batch_size = 2
            arguments.users, arguments.frames, arguments.m_z, arguments.m_y = 2, 2, 1, 2
            # Phase epochs remain configurable, including in bounded smoke runs.
        else:
            if arguments.train_samples is None:
                arguments.train_samples = 512 if arguments.preliminary else 10001
            if arguments.validation_samples is None:
                arguments.validation_samples = 64 if arguments.preliminary else 128
        if arguments.tensor_cache_mib is None:
            arguments.tensor_cache_mib = 4096 if arguments.preliminary else 0
        arguments.output = arguments.output.resolve()
    return arguments, resumed


def save_training_boundary(
    path,
    model,
    *,
    arguments,
    source,
    recipe,
    recipe_sha,
    gamma_fit,
    initial_state_sha,
    history,
    next_task,
    completed_phases,
    elapsed_seconds,
    resume_count,
    cache_statistics=None,
):
    saved_arguments = {
        key: value
        for key, value in vars(arguments).items()
        if key not in ("resume", "stop_after_phase")
    }
    saved_arguments["output"] = str(arguments.output)
    numpy_rng = np.random.get_state()
    payload = dict(
        schema=TRAINING_STATE_SCHEMA,
        method=METHOD,
        arguments=saved_arguments,
        source=source,
        recipe=recipe,
        training_recipe_sha256=recipe_sha,
        gamma_fit=gamma_fit,
        state_dict=model.state_dict(),
        model_state_sha256=state_sha(model),
        initial_state_sha256=initial_state_sha,
        history=history,
        next_task=next_task,
        completed_training_phases=completed_phases,
        elapsed_seconds=elapsed_seconds,
        resume_count=resume_count,
        torch_rng_state=torch.get_rng_state(),
        numpy_rng_state=dict(
            generator=numpy_rng[0],
            keys=numpy_rng[1].tolist(),
            position=numpy_rng[2],
            has_gauss=numpy_rng[3],
            cached_gaussian=numpy_rng[4],
        ),
        training_completed=False,
        resume_boundary="completed phase or layer validation",
        optimizer_state="fresh Adam at the next phase; no mid-phase resume",
        tensor_cache_statistics=cache_statistics,
        cache_tensors_persisted=False,
    )
    temporary = path.with_suffix(".pt.tmp")
    torch.save(payload, temporary)
    temporary.replace(path)
    write_json(arguments.output / "HISTORY.json", history)
    status = (
        "SMOKE_CHECKPOINTED"
        if arguments.smoke
        else "PRELIMINARY_CHECKPOINTED" if arguments.preliminary else "TRAINING_CHECKPOINTED"
    )
    progress = dict(
        status=status,
        training_completed=False,
        completed_training_phases=completed_phases,
        next_task=next_task,
        state_sha256=payload["model_state_sha256"],
        checkpoint_path=str(path),
        checkpoint_sha256=sha256(path),
        training_recipe_sha256=recipe_sha,
        resume_count=resume_count,
        seconds=elapsed_seconds,
        formal_qualification=False,
        threshold_calibrated=False,
        tensor_cache_statistics=cache_statistics,
    )
    write_json(arguments.output / "STATUS.json", progress)
    return progress


def main(argv=None):
    arguments, resumed = resolve_arguments(argv)
    positive = (
        arguments.train_samples,
        arguments.validation_samples,
        arguments.batch_size,
        arguments.microbatch_size,
        arguments.gnn_epochs,
        arguments.damping_epochs,
        arguments.joint_epochs,
        arguments.threads,
    )
    if any(x < 1 for x in positive) or arguments.microbatch_size > arguments.batch_size:
        raise ValueError("positive sample/batch/epoch/thread counts and microbatch<=batch required")
    if arguments.tensor_cache_mib < 0:
        raise ValueError("nonnegative tensor-cache-mib required")
    if arguments.preliminary and (
        not 128 <= arguments.train_samples <= 10000 or arguments.batch_size != 128
    ):
        raise ValueError(
            "preliminary training requires 128..10000 real samples and effective batch size 128"
        )
    if (
        not arguments.smoke
        and not arguments.preliminary
        and (arguments.train_samples <= 10000 or arguments.batch_size != 128)
    ):
        raise ValueError(
            "paper-recipe full training requires >10000 samples and batch size 128; use --smoke for checks"
        )
    if not np.isfinite(arguments.learning_rate) or arguments.learning_rate <= 0:
        raise ValueError("positive finite learning rate required")
    if arguments.stop_after_phase is not None and not 1 <= arguments.stop_after_phase <= 29:
        raise ValueError("stop-after-phase must identify one of the 29 effective training phases")
    train_seeds = list(
        range(arguments.train_seed_base, arguments.train_seed_base + arguments.train_samples)
    )
    validation_seeds = list(
        range(
            arguments.validation_seed_base,
            arguments.validation_seed_base + arguments.validation_samples,
        )
    )
    if min(train_seeds + validation_seeds) < 0 or set(train_seeds) & set(validation_seeds):
        raise ValueError("nonnegative disjoint training and validation seeds required")
    source = source_identity()
    recipe, recipe_sha = recipe_identity(arguments)
    if resumed is None:
        if arguments.output.exists():
            raise ValueError("fresh training output directory required")
        arguments.output.mkdir(parents=True)
    else:
        if resumed["source"] != source:
            raise ValueError(
                "resume source/runtime identity differs from the recorded training sources"
            )
        if resumed["recipe"] != recipe or resumed["training_recipe_sha256"] != recipe_sha:
            raise ValueError("resume training recipe identity is inconsistent")
        plan_on_disk = json.loads((arguments.output / "PLAN.json").read_text())
        if plan_on_disk["training_recipe_sha256"] != recipe_sha or plan_on_disk["source"] != source:
            raise ValueError("resume plan is inconsistent with the saved recipe and sources")
        if (
            arguments.stop_after_phase is not None
            and arguments.stop_after_phase <= resumed["completed_training_phases"]
        ):
            raise ValueError("stop-after-phase must follow the already completed boundary")
    torch.set_num_threads(arguments.threads)
    torch.manual_seed(arguments.model_seed)
    np.random.seed(arguments.model_seed)
    start = time.perf_counter()
    plan = {
        key: value
        for key, value in vars(arguments).items()
        if key not in ("resume", "stop_after_phase")
    }
    plan["output"] = str(arguments.output)
    contract = data_contract(arguments)
    plan.update(
        status=(
            "SMOKE_ONLY"
            if arguments.smoke
            else "PRELIMINARY_TRAINING" if arguments.preliminary else "TRAINING"
        ),
        source=source,
        train_seeds=train_seeds,
        validation_seeds=validation_seeds,
        seed_sets_disjoint=True,
        generator_version=contract["generator_version"],
        dictionary=INTEGER_GRID,
        architecture=asdict(GNNASPLSettings()),
        effective_gnn_updates=9,
        objective="sample-average physical coefficient NMSE, Ding Eq.(28)",
        data_contract=contract,
        continuous_channel_adaptation=(
            "oracle projection labels; actual continuous observation retained"
            if contract["continuous_projection_labels"]
            else "physical on-grid scene; exact finite-dictionary coefficient labels"
        ),
        graph="same-user fully connected including self",
        slab_mean=0.0,
        gradient_accumulation=True,
        optimizer="Adam",
        optimizer_reset_each_phase=True,
        device="cpu",
        precision="complex64/float32",
        torch_version=str(torch.__version__),
        public_noise="fixed generation complex variance; no oracle projection residual correction",
        formal_qualification=False,
        threshold_calibrated=False,
        mainline_changed=False,
        recipe=recipe,
        training_recipe_sha256=recipe_sha,
        resume_boundary="completed phase or layer validation",
        tensor_cache=dict(
            limit_mib=arguments.tensor_cache_mib,
            kind="bounded deterministic RAM LRU",
            changes_generated_arrays=False,
            checkpointed_tensors=False,
        ),
        interrupted_phase_policy="rerun the unfinished phase from its saved preceding boundary",
    )
    if resumed is None:
        write_json(arguments.output / "PLAN.json", plan)
    try:
        atoms, _, _ = physical_atoms(**INTEGER_GRID)
        # Verify the oracle projection identity once before streaming labels.
        project_channel_coefficients(np.zeros((1, 1, atoms.shape[-1], atoms.shape[-1])), atoms)
        cache = DeterministicTensorCache(arguments.tensor_cache_mib)
        gamma_fit = (
            fit_gamma(arguments, train_seeds, atoms, cache)
            if resumed is None
            else resumed["gamma_fit"]
        )
        if resumed is None:
            write_json(arguments.output / "GAMMA_FIT.json", gamma_fit)
        model = GNNASPLNetwork(gamma_fit["physical_variance"])
        initial_state_sha = state_sha(model) if resumed is None else resumed["initial_state_sha256"]
        history = [] if resumed is None else resumed["history"]
        next_task = 0 if resumed is None else resumed["next_task"]
        completed_phases = 0 if resumed is None else resumed["completed_training_phases"]
        prior_seconds = 0.0 if resumed is None else resumed["elapsed_seconds"]
        resume_count = 0 if resumed is None else resumed["resume_count"] + 1
        if resumed is not None:
            model.load_state_dict(resumed["state_dict"], strict=True)
            if state_sha(model) != resumed["model_state_sha256"]:
                raise ValueError("resume model state differs from the recorded model hash")
            torch.set_rng_state(resumed["torch_rng_state"])
            nr = resumed["numpy_rng_state"]
            np.random.set_state(
                (
                    nr["generator"],
                    np.asarray(nr["keys"], dtype=np.uint32),
                    nr["position"],
                    nr["has_gauss"],
                    nr["cached_gaussian"],
                )
            )
        tasks = phase_schedule(model.settings.layers)
        if not 0 <= next_task <= len(tasks):
            raise ValueError("invalid saved layerwise schedule position")
        state_path = arguments.output / "training_state.pt"
        save_training_boundary(
            state_path,
            model,
            arguments=arguments,
            source=source,
            recipe=recipe,
            recipe_sha=recipe_sha,
            gamma_fit=gamma_fit,
            initial_state_sha=initial_state_sha,
            history=history,
            next_task=next_task,
            completed_phases=completed_phases,
            elapsed_seconds=prior_seconds + time.perf_counter() - start,
            resume_count=resume_count,
            cache_statistics=cache.statistics(),
        )
        for index in range(next_task, len(tasks)):
            layers, phase = tasks[index]["layer"], tasks[index]["phase"]
            if phase == "validation":
                validation_nmse = validate(model, arguments, validation_seeds, atoms, layers, cache)
                history.append(
                    dict(layer=layers, phase="validation", coefficient_nmse=validation_nmse)
                )
            else:
                records = train_phase(
                    model,
                    arguments,
                    train_seeds,
                    atoms,
                    layers,
                    phase,
                    getattr(arguments, phase + "_epochs"),
                    cache,
                )
                history.extend(records)
                completed_phases += 1
                print(json.dumps(records[-1]), flush=True)
            progress = save_training_boundary(
                state_path,
                model,
                arguments=arguments,
                source=source,
                recipe=recipe,
                recipe_sha=recipe_sha,
                gamma_fit=gamma_fit,
                initial_state_sha=initial_state_sha,
                history=history,
                next_task=index + 1,
                completed_phases=completed_phases,
                elapsed_seconds=prior_seconds + time.perf_counter() - start,
                resume_count=resume_count,
                cache_statistics=cache.statistics(),
            )
            if phase != "validation" and completed_phases == arguments.stop_after_phase:
                print(json.dumps(progress), flush=True)
                return progress
        validation_nmse = history[-1]["coefficient_nmse"]
        training = dict(
            status=(
                "SMOKE_ONLY"
                if arguments.smoke
                else "PRELIMINARY_TRAINED" if arguments.preliminary else "TRAINED_UNQUALIFIED"
            ),
            training_completed=True,
            snr_db=arguments.snr_db,
            separate_model_per_snr=True,
            training_samples=len(train_seeds),
            validation_samples=len(validation_seeds),
            train_seeds=train_seeds,
            validation_seeds=validation_seeds,
            validation_role="fixed held-out development checks; no threshold/calibration fit",
            final_validation_coefficient_nmse=validation_nmse,
            epochs=dict(
                gnn=arguments.gnn_epochs,
                damping=arguments.damping_epochs,
                joint=arguments.joint_epochs,
            ),
            optimizer="Adam",
            initial_learning_rate=arguments.learning_rate,
            effective_batch_size=arguments.batch_size,
            microbatch_size=arguments.microbatch_size,
            model_seed=arguments.model_seed,
            generator_version=contract["generator_version"],
            grid_mode=grid_mode(arguments),
            data_contract=contract,
            scenario=dict(
                users=arguments.users,
                frames=arguments.frames,
                m_z=arguments.m_z,
                m_y=arguments.m_y,
                activity_probability=arguments.activity_probability,
                require_active_user=True,
                scale=arguments.scale,
            ),
            initial_state_sha256=initial_state_sha,
            final_state_sha256=state_sha(model),
            seconds=prior_seconds + time.perf_counter() - start,
            formal_qualification=False,
            completed_training_phases=completed_phases,
            resume_count=resume_count,
            training_recipe_sha256=recipe_sha,
            preliminary=arguments.preliminary,
            tensor_cache_statistics=cache.statistics(),
            training_budget_scope=(
                "declared smaller-than-paper preliminary training"
                if arguments.preliminary
                else "bounded smoke only" if arguments.smoke else "paper sample/batch budget"
            ),
            source_equations_corrected=True,
            continuous_projection_labels=contract["continuous_projection_labels"],
        )
        checkpoint = arguments.output / "checkpoint.pt"
        torch.save(
            dict(
                schema=CHECKPOINT_SCHEMA,
                method=METHOD,
                architecture=asdict(model.settings),
                state_dict=model.state_dict(),
                gamma_fit=gamma_fit,
                dictionary=INTEGER_GRID,
                training=training,
                source=source,
                training_recipe=recipe,
                training_recipe_sha256=recipe_sha,
            ),
            checkpoint,
        )
        training.update(checkpoint_path=str(checkpoint), checkpoint_sha256=sha256(checkpoint))
        write_json(arguments.output / "STATUS.json", training)
        print(
            json.dumps(
                dict(
                    status=training["status"],
                    checkpoint=str(checkpoint),
                    checkpoint_sha256=training["checkpoint_sha256"],
                    validation_coefficient_nmse=validation_nmse,
                    seconds=training["seconds"],
                )
            ),
            flush=True,
        )
        return training
    except BaseException as exc:
        write_json(
            arguments.output / "FAILURE.json",
            dict(status="FAILED", exception=type(exc).__name__, message=str(exc)),
        )
        raise


if __name__ == "__main__":
    main()
