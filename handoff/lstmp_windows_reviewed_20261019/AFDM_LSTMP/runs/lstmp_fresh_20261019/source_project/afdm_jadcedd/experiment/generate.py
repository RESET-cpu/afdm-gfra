"""Geometry-consistent AFDM scenes, receiver inputs and separate truth records.

The application saves only the four ReceiverInput fields. The extra directions
in the in-memory inputs remain available for archived known-direction controls.
"""
from dataclasses import replace
import numpy as np

from afdm_jadcedd.system.core.upa import steering_vector_operator
from afdm_jadcedd.system.phase import phase_operator, wrap
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.observation import array_sha256
from afdm_jadcedd.system.pilot import PartialDFTPilot
from afdm_jadcedd.system.scenario.continuous import full_h_and_phase
from afdm_jadcedd.system.scenario.geometry_consistent import draw_scene
from afdm_jadcedd.system.core.config import ArrayConfig

GENERATOR_VERSION = 'known_phase_geometry_v4'
LEGACY_GENERATOR_VERSION = 'known_phase_geometry_v3'
CONDITION_GENERATOR_VERSION = 'known_phase_geometry_v5_conditions'
FIXED_ACTIVITY_GENERATOR_VERSION = 'known_phase_geometry_v6_fixed_activity'


def _condition_scene(scene, *, grid_mode, rician_k_db):
    """Transform an existing draw without consuming any random numbers.

    K is the TDL-D co-located LOS/Rayleigh power ratio of paths 0 and 1,
    not the LOS/total-NLOS ratio. Their summed expected power is preserved;
    the two delayed Rayleigh paths and every underlying fading draw stay fixed.
    """
    training_k_db = float(cfg.RICIAN_K_DB)
    target_k_db = training_k_db if rician_k_db is None else float(rician_k_db)
    original_powers = np.power(10., np.asarray(cfg.NTN_TDL_D_POWER_DB)/10.)
    powers = original_powers.copy()
    change_k = target_k_db != training_k_db
    if change_k:
        if (cfg.NTN_TDL_D_FADING[:2] != ('los', 'rayleigh') or
                cfg.NTN_TDL_D_NORMALIZED_DELAYS[:2] != (0., 0.)):
            raise ValueError('Rician condition requires co-located TDL-D LOS/Rayleigh paths')
        # A stable power split also covers large finite positive/negative K dB.
        log_k = target_k_db/10.*np.log(10.)
        pair_power = float(original_powers[:2].sum())
        powers[0] = pair_power*np.exp(-np.logaddexp(0., -log_k))
        powers[1] = pair_power*np.exp(-np.logaddexp(0., log_k))
    scales = np.sqrt(powers/original_powers)
    limit = int(np.floor(cfg.TAU_MAX_S*cfg.BANDWIDTH_HZ))
    transformed, records, clipped = [], [], 0
    for path in scene.paths:
        full_delay = float(path.delay_s*cfg.BANDWIDTH_HZ)
        delay, frequency = full_delay, float(path.doppler_hz)
        candidate = path
        if grid_mode == 'on_grid':
            nearest = float(np.rint(full_delay))
            delay = float(np.clip(nearest, 0, limit))
            clipped += int(delay != nearest)
            frequency = float(np.rint(frequency/cfg.DELTA_F_HZ)*cfg.DELTA_F_HZ)
            # Store the complete quantized delay. Reducing it modulo N here
            # would discard the CPP phase of the original physical period.
            candidate = replace(candidate, macro_delay_s=delay/cfg.BANDWIDTH_HZ,
                                normalized_delay=0., doppler_hz=frequency)
        if change_k and path.path_id < 2:
            candidate = replace(candidate, gain=path.gain*scales[path.path_id])
        transformed.append(candidate)
        records.append(dict(user_id=int(path.user_id), path_id=int(path.path_id),
            original_macro_delay_s=float(path.macro_delay_s),
            original_normalized_delay=float(path.normalized_delay),
            original_delay_spread_s=float(path.delay_spread_s),
            original_delay_s=float(path.delay_s), delay_s=float(candidate.delay_s),
            original_full_delay_samples=full_delay, full_delay_samples=delay,
            original_delay_period=int(np.floor(full_delay/cfg.N)),
            delay_period=int(np.floor(delay/cfg.N)), folded_delay_samples=float(delay % cfg.N),
            original_doppler_hz=float(path.doppler_hz), doppler_hz=frequency,
            original_gain=[float(path.gain.real), float(path.gain.imag)],
            gain=[float(candidate.gain.real), float(candidate.gain.imag)],
            mu_z=float(candidate.mu_z), mu_y=float(candidate.mu_y)))
    details = dict(version=CONDITION_GENERATOR_VERSION, grid_mode=grid_mode,
        training_rician_k_db=training_k_db, rician_k_db=target_k_db,
        rician_k_changed=change_k,
        rician_scope='TDL-D co-located paths 0 (LOS) and 1 (Rayleigh); pair expected power fixed',
        training_path_expected_powers=original_powers.tolist(),
        path_expected_powers=powers.tolist(), path_gain_amplitude_scales=scales.tolist(),
        delay_grid_step_samples=1., doppler_grid_step_hz=float(cfg.DELTA_F_HZ),
        delay_grid_max_samples=limit,
        rounding='nearest integer, ties to even; delay clipped to physical-support integer endpoints',
        delay_boundary_clipped_paths=clipped,
        geometry_scope='original physical geometry; on_grid is its paired parameter projection',
        path_parameters=records)
    return replace(scene, paths=tuple(transformed)), details


def _draw_nonempty_activity(seed, users, probability):
    """Condition the original activity stream on at least one transmission."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, 7102]))
    draws = 0
    while True:
        draws += 1
        activity = (rng.random(users) < probability).astype(np.int64)
        if activity.any():
            return activity, draws


def _draw_fixed_activity(seed, users, active_users):
    """Uniform fixed-size subset, independent of every physical-channel draw.

    A common permutation pairs load comparisons by nesting their active sets.
    The receiver's marginal probability is active_users/users; the indicators
    are dependent because their sum is fixed.
    """
    if (isinstance(active_users, (bool, np.bool_))
            or not isinstance(active_users, (int, np.integer))
            or not 1 <= active_users < users):
        raise ValueError('fixed_active_users must be an integer between 1 and users-1')
    rng = np.random.default_rng(np.random.SeedSequence([seed, 7102]))
    activity = np.zeros(users, dtype=np.int64)
    activity[rng.permutation(users)[:active_users]] = 1
    return activity


def generate_case(seed, snr_db, scale, *, activity_probability=.1, users=40,
                  frames=16, m_z=4, m_y=4, spread_range_s=(30e-9, 50e-9),
                  path_direction_rms_deg=0., require_active_user=True,
                  grid_mode='off_grid', rician_k_db=None, fixed_active_users=None):
    """Preserve exact cross-frame phase and the received-SNR convention.

    Truth is returned separately and is needed only to construct and score a
    simulated experiment. Directions are evaluation metadata and are removed
    when constructing the four-field ReceiverInput. Current experiments require
    a transmission; False reproduces the historical unconditioned generator.
    The public activity prior is the conditional marginal, not a realized count.

    off_grid and the default K preserve the original generator exactly. on_grid
    rounds full physical delays to the nearest supported integer sample (never
    modulo N), and Doppler/DELTA_F_HZ to its nearest integer. Changing K only
    splits the fixed total expected power of the co-located TDL-D LOS/Rayleigh
    pair; delayed paths, fading phases, pilots and standard noise draws stay
    paired. The received-SNR noise variance is recomputed from the changed H.

    fixed_active_users selects a uniform subset of that size, independently of
    fading and geometry. Its marginal replaces activity_probability, which
    applies only to the Bernoulli mode. Omitting it preserves existing draws
    and metadata. No cardinality constraint is added to receiver decisions.
    """
    if not np.isfinite(scale) or scale <= 0 or not np.isfinite(snr_db):
        raise ValueError('finite SNR and positive global physical scale required')
    if any(isinstance(x, bool) or not isinstance(x, (int, np.integer)) or x < 1
           for x in (users, frames, m_z, m_y)) or frames > 32:
        raise ValueError('positive integer dimensions and at most 32 pilot frames required')
    if not 0 < activity_probability < 1 or not np.isfinite(path_direction_rms_deg) or path_direction_rms_deg < 0:
        raise ValueError('valid activity probability and nonnegative direction spread required')
    if not isinstance(require_active_user, (bool, np.bool_)):
        raise ValueError('require_active_user must be boolean')
    if require_active_user and users < 2:
        raise ValueError('at least two candidates required for nontrivial activity detection')
    if fixed_active_users is not None and (
            isinstance(fixed_active_users, (bool, np.bool_))
            or not isinstance(fixed_active_users, (int, np.integer))
            or not 1 <= fixed_active_users < users):
        raise ValueError('fixed_active_users must be an integer between 1 and users-1')
    if grid_mode not in ('off_grid', 'on_grid'):
        raise ValueError('grid_mode must be off_grid or on_grid')
    if rician_k_db is not None and (isinstance(rician_k_db, (bool, np.bool_)) or
            not isinstance(rician_k_db, (int, float, np.integer, np.floating)) or
            not np.isfinite(rician_k_db)):
        raise ValueError('rician_k_db must be a finite dB value or None')
    array = ArrayConfig(M_z=m_z, M_y=m_y)
    scene, geometry = draw_scene(seed, n_users=users, activity_probability=activity_probability,
                                spread_range_s=spread_range_s)
    activity_draws = 1
    nonempty_probability = float(-np.expm1(users*np.log1p(-activity_probability)))
    activity_prior = activity_probability
    if fixed_active_users is not None:
        scene = replace(scene, activity=_draw_fixed_activity(seed, users, fixed_active_users))
        activity_prior = fixed_active_users/users
        nonempty_probability = 1.
    elif require_active_user:
        activity, activity_draws = _draw_nonempty_activity(seed, users, activity_probability)
        scene = replace(scene, activity=activity)
        activity_prior = activity_probability/nonempty_probability
    if path_direction_rms_deg:
        # Controlled NLOS departure from the common-direction model. Keep the
        # LOS direction, delays, Dopplers and gains fixed for this comparison.
        paths = []
        for path in scene.paths:
            if path.path_id == 0:
                paths.append(path)
                continue
            look = geometry.look[path.user_id]
            ref = np.array([0., 0., 1.]) if abs(look[2]) < .9 else np.array([0., 1., 0.])
            tangent = np.cross(look, ref); tangent /= np.linalg.norm(tangent)
            second = np.cross(look, tangent)
            rng = np.random.default_rng(np.random.SeedSequence([seed, 7210, path.user_id, path.path_id]))
            delta = rng.normal(size=2)*np.deg2rad(path_direction_rms_deg)/np.sqrt(2)
            radius = np.linalg.norm(delta)
            ray = np.cos(radius)*look + np.sinc(radius/np.pi)*(delta[0]*tangent+delta[1]*second)
            local = geometry.array_axes@ray
            paths.append(replace(path, mu_z=float(local[2]), mu_y=float(local[1])))
        scene = replace(scene, paths=tuple(paths))
    condition_metadata = None
    condition_changed = (grid_mode != 'off_grid' or
                         (rician_k_db is not None and float(rician_k_db) != cfg.RICIAN_K_DB))
    # Explicit default-K calls retain v4 numerical results, while still recording
    # their requested condition. Omitted options retain the original metadata.
    if grid_mode != 'off_grid' or rician_k_db is not None:
        scene, condition_metadata = _condition_scene(
            scene, grid_mode=grid_mode, rician_k_db=rician_k_db)
    h, _ = full_h_and_phase(scene, frames, array=array)
    directions = np.stack([steering_vector_operator(array, p.mu_z, p.mu_y)
                           for p in (scene.paths_of(k)[0] for k in range(users))])
    base_pilot = PartialDFTPilot(users, frames, seed + 10**12,
                                input_size=cfg.N).dense().reshape(frames, users, cfg.N)
    doppler = np.array([scene.paths_of(k)[0].doppler_hz for k in range(users)])
    slopes = wrap(2 * np.pi * doppler * (cfg.N + cfg.N_CPP) / cfg.BANDWIDTH_HZ)
    operator = phase_operator(base_pilot, slopes)
    clean = np.einsum('qkn,kmrn->qmr', operator, h, optimize=False)
    power = float(np.mean(abs(clean)**2))
    if require_active_user and (not np.isfinite(power) or power <= 0):
        raise FloatingPointError('nonempty scene must have positive finite clean received power')
    reference = power if scene.activity.any() else scale**2 * users * activity_probability
    if reference <= 0:
        reference = scale**2 * users * .1
    noise = reference * 10**(-float(snr_db) / 10)
    rng = np.random.default_rng(np.random.SeedSequence([seed, 2096]))
    shape = (32, array.M, cfg.N)
    epsilon = ((rng.normal(size=shape) + 1j * rng.normal(size=shape)) / np.sqrt(2))[:frames]
    inputs = dict(observation=clean + np.sqrt(noise) * epsilon, operator=operator,
                  noise_variance=noise, activity_prior=activity_prior, directions=directions)
    truth = dict(channel=h, activity=scene.activity, phase_slopes=slopes, doppler_hz=doppler)
    metadata = dict(generator_version=GENERATOR_VERSION if require_active_user else LEGACY_GENERATOR_VERSION,
        seed=int(seed), snr_db=float(snr_db),
        users=users, frames=frames, m_z=m_z, m_y=m_y,
        spread_range_s=list(spread_range_s), path_direction_rms_deg=path_direction_rms_deg,
        direction_spread_scope='independent tangent-plane Gaussian NLOS deviations; LOS and common Doppler fixed',
        activity_probability=activity_probability, physical_clean_power=power,
        require_active_user=bool(require_active_user), activity_draws=activity_draws,
        activity_sampling='independent Bernoulli vectors conditioned on at least one active user'
            if require_active_user else 'independent Bernoulli vectors',
        unconditioned_nonempty_probability=nonempty_probability,
        activity_prior=activity_prior, expected_active_users=users*activity_prior,
        active_users=int(scene.activity.sum()),
        phase_scope='exact known effective operator, retained by user instruction',
        array_frame='fixed nadir-normal UPA; y=global Y; z=global X; identical for all candidates',
        satellite_position=geometry.satellite.tolist(), satellite_velocity=geometry.velocity.tolist(),
        ground_positions=geometry.ground.tolist(), array_axes=geometry.array_axes.tolist(),
        direction_cosines=geometry.direction_cosines.tolist(), look_vectors=geometry.look.tolist(),
        reference_delay_s=geometry.reference_delay_s,
        noise_reference='complete noiseless received power after phase' if require_active_user else
            'complete noiseless received power after phase; fixed-population fallback for empty scenes',
        standardized_noise_sha256=array_sha256(epsilon), noise_variance=noise)
    if condition_metadata is not None:
        metadata['scene_conditions'] = condition_metadata
        metadata['base_pilot_sha256'] = array_sha256(base_pilot)
        metadata['base_generator_version'] = metadata['generator_version']
        if condition_changed:
            metadata['generator_version'] = CONDITION_GENERATOR_VERSION
    if fixed_active_users is not None:
        metadata.update(base_generator_version=metadata['generator_version'],
            generator_version=FIXED_ACTIVITY_GENERATOR_VERSION,
            fixed_active_users=int(fixed_active_users),
            activity_probability=float(activity_prior),
            activity_sampling='uniform subset of fixed size, independent of physical channels',
            activity_dependence='fixed total count; marginal probability fixed_active_users/users',
            activity_pairing='prefix of the same candidate permutation across fixed counts',
            receiver_cardinality_constraint=False)
    return inputs, truth, metadata
