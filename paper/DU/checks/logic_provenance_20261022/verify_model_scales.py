"""Small deterministic checks for the manuscript's model discussion.

This is an analytic scale calculation, not a channel-tracking experiment.
It reads the frozen physical constants without modifying any configuration.
"""
from pathlib import Path
import ast
import json
import math
import numpy as np

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def literal_constants(path):
    values = {}
    for node in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            if isinstance(node.targets[0], ast.Name):
                try:
                    values[node.targets[0].id] = ast.literal_eval(node.value)
                except (ValueError, TypeError):
                    pass
    return values


cfg = literal_constants(ROOT / "src/system/config.py")
geo = literal_constants(ROOT / "src/system/scenario/scene_generator.py")
c0 = literal_constants(ROOT / "src/system/scenario/geometry.py")["C_LIGHT_M_S"]
n = cfg["N"]
ts = 1.0 / (n * cfg["DELTA_F_HZ"])
n_cpp = math.ceil(cfg["TAU_MAX_S"] / ts)
t_frame = (n + n_cpp) * ts
radius = cfg["EARTH_RADIUS_M"] + cfg["ORBIT_ALTITUDE_M"]
speed = math.sqrt(geo["MU_EARTH"] / radius)
acceleration = speed**2 / radius
# From nu = -(fc/c0) u^T v, d >= orbital altitude, and circular motion:
nu_rate_bound = cfg["CARRIER_HZ"] / c0 * (
    speed**2 / cfg["ORBIT_ALTITUDE_M"] + acceleration
)
rows = []
for q in [8, 16, 24, 32, 40, 48]:
    duration = q * t_frame
    # nu_max bounds the initial Doppler; integrate the derivative bound too.
    delay_bound = (
        cfg["NU_MAX_HZ"] * duration + 0.5 * nu_rate_bound * duration**2
    ) / cfg["CARRIER_HZ"]
    rows.append({
        "frames": q,
        "block_ms": duration * 1e3,
        "delay_change_bound_us": delay_bound * 1e6,
        "delay_change_bound_samples": delay_bound / ts,
        "doppler_change_bound_hz": nu_rate_bound * duration,
        "constant_doppler_phase_error_bound_rad": math.pi * nu_rate_bound * duration**2,
    })

# A finite-difference check of the derivative identity at fixed ground points.
dt = 1e-3
omega = speed / radius
sat0 = np.array([0., 0., radius])
vel0 = np.array([speed, 0., 0.])
acc0 = np.array([0., 0., -acceleration])
derivative_errors = []
for gamma in [0., 0.03, 0.06, 0.1]:
    ground = cfg["EARTH_RADIUS_M"] * np.array([math.sin(gamma), 0., math.cos(gamma)])
    ray = ground - sat0
    distance = np.linalg.norm(ray)
    unit = ray / distance
    analytic = cfg["CARRIER_HZ"] / c0 * (
        (speed**2 - (unit @ vel0)**2) / distance - unit @ acc0
    )
    def doppler(t):
        sat = radius * np.array([math.sin(omega*t), 0., math.cos(omega*t)])
        vel = speed * np.array([math.cos(omega*t), 0., -math.sin(omega*t)])
        look = ground - sat
        look /= np.linalg.norm(look)
        return -cfg["CARRIER_HZ"] / c0 * (look @ vel)
    finite = (doppler(dt) - doppler(-dt)) / (2*dt)
    derivative_errors.append(abs(analytic-finite))
    assert abs(analytic) <= nu_rate_bound
assert max(derivative_errors) < 1e-4

# A small numerical illustration of the exact row-Gram identity.
rng = np.random.default_rng(20261022)
k, side, frames = 4, 8, 6
j = k*side
rr = rng.choice(j, frames, replace=False)
cc = rng.permutation(j)
pilot = np.exp(-2j*np.pi*rr[:,None]*cc[None,:]/j)
pilot *= np.exp(1j*rng.uniform(-np.pi,np.pi,j))[None,:]
beta = rng.uniform(-np.pi,np.pi,k)
a = pilot * np.exp(1j*np.arange(frames)[:,None]*np.repeat(beta,side)[None,:])
identity = np.empty((frames,frames),complex)
for q in range(frames):
    for qp in range(frames):
        identity[q,qp] = np.sum(
            pilot[q]*pilot[qp].conj()*np.exp(1j*(q-qp)*np.repeat(beta,side)))
assert np.max(np.abs(identity-a@a.conj().T)) < 1e-10
assert np.max(np.abs(pilot@pilot.conj().T-j*np.eye(frames))) < 1e-10

report = {
    "kind": "analytic bounds and deterministic identity checks; no performance experiment",
    "assumptions": [
        "fixed ground terminal, circular orbit, fixed common reference delay within the block",
        "constant excess path delays and gains remain assumptions of the manuscript",
        "Doppler bound NU_MAX_HZ applies at the reference time; variation is bounded separately",
    ],
    "parameters": {"N": n, "N_CPP": n_cpp, "sample_us":ts*1e6,
                   "frame_ms": t_frame*1e3, "speed_m_s": speed,
                   "doppler_rate_bound_hz_s":nu_rate_bound},
    "block_scales": rows,
    "max_doppler_derivative_check_error_hz_s": max(derivative_errors),
    "pilot_gram_error":float(np.max(np.abs(pilot@pilot.conj().T-j*np.eye(frames)))),
    "effective_pilot_gram_identity_error":float(np.max(np.abs(identity-a@a.conj().T))),
    "effective_pilot_max_normalized_offdiagonal":float(np.max(np.abs(a@a.conj().T-j*np.eye(frames)))/j),
}
(OUT/"model_scale_check.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps(report,indent=2))
