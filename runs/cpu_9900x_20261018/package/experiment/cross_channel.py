"""Fixed-weight generalization across NTN-TDL power-delay profiles."""
from dataclasses import replace
from pathlib import Path
import argparse
import numpy as np

from _common import (ROOT, METHODS, LABELS, CONFIGS, read, save, identities, validate,
                     run, summarize, generate_case, phase_operator, DEFAULTS, SNR_VALUES, bind_receivers)
from afdm_jadcedd.system import config as cfg
from afdm_jadcedd.system.scenario.geometry_consistent import draw_scene
from afdm_jadcedd.system.scenario.continuous import full_h_and_phase
from afdm_jadcedd.system.observation import array_sha256

# 3GPP TR 38.811 V15.3.0, §6.9.2, Tables 6.9.2-1 to -4, printed pp.89–90.
# Each row is normalized delay, relative power in dB, fading component.
SOURCE = 'https://atisorg.s3.amazonaws.com/archive/3gpp-documents/Rel15/ATIS.3GPP.38.811.V1530.pdf'
PROFILES = {
    'A': [(0., 0., 'rayleigh'), (1.0811, -4.675, 'rayleigh'), (2.8416, -6.482, 'rayleigh')],
    'B': [(0., 0., 'rayleigh'), (.7249, -1.973, 'rayleigh'), (.7410, -4.332, 'rayleigh'),
          (5.7392, -11.914, 'rayleigh')],
    'C': [(0., -.394, 'los'), (0., -10.618, 'rayleigh'), (14.8124, -23.373, 'rayleigh')],
    'D': [(0., -.284, 'los'), (0., -11.991, 'rayleigh'), (.5596, -9.887, 'rayleigh'),
          (7.3340, -16.771, 'rayleigh')],
}
EXPERIMENT = dict(DEFAULTS, description=__doc__, variable='channel_model', xlabel='SNR (dB)',
                  profiles=['D', 'A', 'B', 'C'], snr=list(SNR_VALUES),
                  seed=202610180600001, methods=METHODS)


def profile_scene(seed, profile, *, users=40, activity_probability=.1):
    """Keep geometry; apply tabulated relative tap powers and delay scaling.

    A/B/C use independent fading streams; D is the exact original sampler.
    Match total expected tap power to D, without per-realization normalization.
    Common per-user satellite Doppler and direction remain the project model;
    this does not simulate the full time-varying terrestrial Doppler spectrum.
    """
    if profile not in PROFILES:
        raise ValueError('Expected NTN-TDL-A/B/C/D')
    scene, geometry = draw_scene(seed, n_users=users, activity_probability=activity_probability)
    reference_power = float(np.sum(10.**(np.asarray(cfg.NTN_TDL_D_POWER_DB)/10)))
    rows = PROFILES[profile]
    factor = reference_power / sum(10.**(db/10) for _, db, _ in rows)
    if profile == 'D':
        if rows != list(zip(cfg.NTN_TDL_D_NORMALIZED_DELAYS, cfg.NTN_TDL_D_POWER_DB, cfg.NTN_TDL_D_FADING)):
            raise ValueError('Mainline D profile differs from the cited table')
        return scene, factor
    paths = []
    for user in range(users):
        base = scene.paths_of(user)[0]
        for index, (delay, db, fading) in enumerate(rows):
            rng = np.random.default_rng(np.random.SeedSequence([seed, 8220, user, index]))
            unit = np.exp(1j*rng.uniform(0, 2*np.pi)) if fading == 'los' else (
                rng.normal()+1j*rng.normal())/np.sqrt(2)
            gain = np.sqrt(factor*10.**(db/10))*unit
            path = replace(base, path_id=index, normalized_delay=delay,
                           gain=complex(gain), legacy_gain=complex(gain))
            if path.delay_s > cfg.TAU_MAX_S:
                raise ValueError('Profile exceeds declared physical delay support; do not clip or reject-sample')
            paths.append(path)
    return replace(scene, paths=tuple(paths)), factor


def generate_profile_case(seed, snr_db, scale, *, profile, users=40, frames=16, activity_probability=.1):
    # Original D path is unchanged, including its activity conditioning and RNG.
    public, truth, metadata = generate_case(seed, snr_db, scale, users=users, frames=frames,
                                            activity_probability=activity_probability)
    scene, factor = profile_scene(seed, profile, users=users, activity_probability=activity_probability)
    if profile != 'D':
        scene = replace(scene, activity=truth['activity'].copy())
        h, _ = full_h_and_phase(scene, frames)
        operator = phase_operator(public['pilot'], truth['phase_slopes'])
        clean = np.einsum('qkn,kmrn->qmr', operator, h, optimize=False)
        power = float(np.mean(abs(clean)**2))
        variance = power*10.**(-snr_db/10)
        rng = np.random.default_rng(np.random.SeedSequence([seed, 2096]))
        shape = (32, h.shape[1], cfg.N)
        epsilon = ((rng.normal(size=shape)+1j*rng.normal(size=shape))/np.sqrt(2))[:frames]
        public.update(observation=clean+np.sqrt(variance)*epsilon, noise_variance=variance)
        truth = dict(truth, channel=h)
        metadata.update(generator_version='experiment_ntn_tdl_profiles_v1', physical_clean_power=power,
                        noise_variance=variance, standardized_noise_sha256=array_sha256(epsilon))
    metadata.update(channel_model='NTN-TDL-'+profile, profile_source=SOURCE,
                    profile_table='6.9.2-'+str('ABCD'.index(profile)+1),
                    profile_components=PROFILES[profile], expected_tap_power_scale=factor,
                    profile_scope='Tabulated power-delay/fading profile in the fixed project geometry; common direction and satellite Doppler',
                    power_policy='Match total expected tap power to frozen D; never normalize individual channels',
                    cross_profile_pairing='Same geometry, activity, pilot and standard noise; D retains original fading stream')
    return public, truth, metadata


def plot_profiles(out, spec, rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, len(spec['profiles']), figsize=(4*len(spec['profiles']), 7),
                             squeeze=False, layout='constrained')
    for col, profile in enumerate(spec['profiles']):
        notes = []
        for method in spec['methods']:
            group = sorted([r for r in rows if r['method'] == method and r['value'].split('/')[0] == profile],
                           key=lambda r: float(r['value'].split('/')[1]))
            x = [float(r['value'].split('/')[1]) for r in group]
            axes[0, col].plot(x, [r['aer'] if r['aer'] else np.nan for r in group], 'o-', label=LABELS[method])
            axes[1, col].plot(x, [r['nmse_db'] for r in group], 'o-', label=LABELS[method])
            zeros = [f'{v:g}' for v, r in zip(x, group) if r['aer'] == 0]
            if zeros:
                notes.append(f'{LABELS[method]}: 0 at '+', '.join(zeros))
        axes[0, col].set_title('NTN-TDL-'+profile)
        axes[0, col].set_yscale('log')
        if not any(r['aer'] > 0 for r in rows if r['value'].split('/')[0] == profile):
            axes[0, col].set_ylim(1e-5, 1)
        if notes:
            axes[0, col].text(.02, .02, '\n'.join(notes), transform=axes[0, col].transAxes, fontsize=6,
                              bbox=dict(facecolor='white', alpha=.9, edgecolor='none'))
        for ax in axes[:, col]:
            ax.set_xlabel('SNR (dB)'); ax.grid(alpha=.25); ax.legend(fontsize=7)
    axes[0, 0].set_ylabel('Activity error rate')
    axes[1, 0].set_ylabel('Full-channel NMSE (dB)')
    fig.suptitle(f'Fixed training weights; {spec["scenes"]} scenes per profile/SNR; estimated phase and noise')
    for suffix in ('png', 'pdf'):
        fig.savefig(out / f'comparison.{suffix}', dpi=180)
    plt.close(fig)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('plan', 'run', 'summarize'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profiles', nargs='+', choices=list(PROFILES), default=EXPERIMENT['profiles'])
    parser.add_argument('--snr', nargs='+', type=float, default=EXPERIMENT['snr'])
    for key in ('scenes', 'seed', 'users', 'frames'):
        parser.add_argument('--'+key, type=int, default=EXPERIMENT[key])
    parser.add_argument('--methods', nargs='+', choices=METHODS, default=METHODS)
    parser.add_argument('--device', choices=('cpu', 'mps', 'auto'), default=EXPERIMENT['device'])
    args = parser.parse_args(argv)
    out = args.output.resolve()
    if args.command == 'plan':
        if out.exists() and any(out.iterdir()):
            raise FileExistsError('Plan requires a fresh output directory')
        spec = dict(EXPERIMENT, **{k:getattr(args, k) for k in
                    ('profiles', 'snr', 'scenes', 'seed', 'users', 'frames', 'methods', 'device')})
        spec.update(values=[f'{p}/{s:g}' for p in args.profiles for s in args.snr],
                    scale=read(ROOT / CONFIGS['proposed'])['scale'])
        if len(set(args.methods)) != len(args.methods):
            parser.error('Distinct methods required')
        validate(spec)
        bind_receivers(spec)
        save(out / 'PLAN.json', dict(experiment=spec, source_and_weight_sha256=identities(),
             profile_source=SOURCE, profile_tables=PROFILES,
             training_sample_comparison='NOT_APPLICABLE', retraining=False,
             expected_runs=spec['scenes']*len(spec['values'])*len(spec['methods'])))
        print(f'PLANNED: {out}'); return 0
    plan = read(out / 'PLAN.json')
    if plan['experiment']['variable'] != 'channel_model':
        raise ValueError('Expected a cross-channel plan')
    return run(out, plan, generator=generate_profile_case, plotter=plot_profiles) if args.command == 'run' else summarize(out, plan['experiment'], plotter=plot_profiles)


if __name__ == '__main__':
    raise SystemExit(main())
