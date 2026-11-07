"""Validate the actual formal sweep union and its training budget."""
import ast
from collections import Counter
from pathlib import Path

from experiments.lstmp_training_v3_20261020.plan import (
    conditions, planned_updates, TRAIN_PER_CONDITION, VALIDATION_PER_CONDITION,
    MAXIMUM_DEPTH, SNR_VALUES)

ROOT = Path(__file__).resolve().parents[1]


def assignment(path, name):
    for node in ast.parse((ROOT / path).read_text(encoding='utf-8')).body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == name for target in node.targets):
            return node.value
    raise AssertionError(f'Missing declaration: {path}/{name}')


def test_conditions_equal_formal_sweeps_not_cartesian_product():
    defaults = assignment('experiment/_support/settings.py', 'DEFAULTS')
    values = {keyword.arg: ast.literal_eval(keyword.value) for keyword in defaults.keywords}
    standard = dict(users=values['users'], frames=values['frames'],
                    activity_probability=values['activity_probability'], snr_db=values['snr_db'])
    formal_snr = list(ast.literal_eval(assignment('experiment/_support/settings.py', 'SNR_VALUES')))
    assert SNR_VALUES == formal_snr == [-4, -2, 0, 2, 4, 6]
    expected = set()
    for field, variants in [('snr_db', formal_snr)] + [
        (field, ast.literal_eval(next(k.value for k in
            assignment('experiment/' + file, 'EXPERIMENT').keywords if k.arg == 'values')))
        for file, field in [('user_count.py', 'users'), ('pilot_frames.py', 'frames'),
                            ('activity_probability.py', 'activity_probability')]
    ]:
        expected.update(tuple(sorted(dict(standard, **{field: item}).items())) for item in variants)
    actual = [tuple(sorted(row.items())) for row in conditions()]
    assert len(actual) == len(set(actual)) == len(expected) == 19
    assert set(actual) == expected
    assert not any(row['users'] == 100 and row['frames'] == 8 for row in conditions())
    for row in conditions():
        if row['snr_db'] != 0:
            assert (row['users'], row['frames'], row['activity_probability']) == (40, 16, .1)


def test_equal_condition_allocation_and_new_training_statistics_counts():
    table = conditions()
    for per_condition in (TRAIN_PER_CONDITION, VALIDATION_PER_CONDITION):
        groups = Counter(tuple(sorted(table[i % len(table)].items()))
                         for i in range(len(table) * per_condition))
        assert len(groups) == 19 and set(groups.values()) == {per_condition}
    assert len(table) * TRAIN_PER_CONDITION == 4750
    assert len(table) * VALIDATION_PER_CONDITION == 1900
    assert sum(row['users'] for row in table) * TRAIN_PER_CONDITION == 215000


def test_ten_layer_budget_and_all_snr_values_represented():
    assert MAXIMUM_DEPTH == 10
    assert planned_updates() == 142500
    assert {row['snr_db'] for row in conditions()} == set(SNR_VALUES)
    assert sum(row['snr_db'] == 0 for row in conditions()) == 14


def test_long_pilot_generation_matches_existing_formal_experiment():
    import numpy as np
    from experiment._common import observation
    from experiments.lstmp_training_v3_20261020.generation import generate_case
    from afdm_jadcedd.experiment.generate import generate_case as original
    from afdm_jadcedd.system.phase import phase_operator
    scale = .2647966452702405
    # Disposable developer checks, disjoint from train/validation/test seeds.
    seed = 202610206900001
    for frames in (8, 32, 40, 48):
        condition = dict(users=40, frames=frames, activity_probability=.1, snr_db=0)
        public, truth, _ = generate_case(seed, 0, scale, users=40, frames=frames)
        formal, formal_truth, metadata = observation(seed, condition, scale)
        np.testing.assert_allclose(public['observation'], formal.observation, rtol=1e-12, atol=1e-12)
        np.testing.assert_array_equal(truth['channel'], formal_truth['channel'])
        np.testing.assert_array_equal(truth['activity'], formal_truth['activity'])
        np.testing.assert_array_equal(public['operator'],
                                      phase_operator(formal.pilot, formal_truth['phase_slopes']))
        np.testing.assert_allclose(public['noise_variance'], metadata['generated_noise_variance'],
                                   rtol=1e-12, atol=0)
        if frames <= 32:
            old, old_truth, _ = original(seed, 0, scale, users=40, frames=frames)
            for key in old:
                np.testing.assert_array_equal(public[key], old[key])
