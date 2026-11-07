"""Deterministic formula audit; no training, receiver benchmark, or source edits.

Source: Bemani thesis, Sec. 3.1.1, Eqs. (3.5), (3.7), (3.9), (3.14);
Huang Eq. (5); manuscript Appendix B. Each comparison is within the
point-sampled analytic waveform model, not a pulse-shaped link validation.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "src"))
from system.afdm.continuous import continuous_path_matrix
from system.afdm.path_operator_multicycle_full import full_delay_path_matrix
from system.afdm.types import FoldedDelay
from system.phase import phase_operator
from system.receiver.phase_atoms import path_atom, sensed_atom
from system import config as cfg

TOLERANCE = 1e-9  # Fixed before the first run; includes long-delay phase roundoff.


def transform(n, c1, c2):
    return np.array([[np.exp(-2j*np.pi*(c2*r*r+r*t/n+c1*t*t))
                      / np.sqrt(n) for t in range(n)] for r in range(n)])


def intervals(n, c1, index):
    c = round(2*n*c1)
    boundaries = [0.] + [(q-index/n)/(2*c1) for q in range(1, c+1)] + [float(n)]
    return list(zip(boundaries[:-1], boundaries[1:]))


def thesis_basis(x, index, n, c1, c2):
    """Continuous intervals, then Eq. 3.7 with the actual Eq. 3.9 phase.

    Recursively apply the one-period CPP relation 3.14 for x < 0.
    Values are normalized by sqrt(sample period) relative to the thesis.
    """
    multiplier = 1.+0j
    while x < 0:
        multiplier *= np.exp(-2j*np.pi*c1*(n*n+2*n*x))
        x += n
    if not 0 <= x < n:
        raise ValueError("Only the useful interval and preceding CPP are needed")
    for q, (lo, hi) in enumerate(intervals(n, c1, index)):
        if lo <= x < hi:
            offset = q*(q-index/n)/(2*c1)
            phi = np.floor(offset)-offset
            phase = c2*index*index+c1*x*x+index*x/n+offset-q*x+phi
            return multiplier*np.exp(2j*np.pi*phase)/np.sqrt(n)
    raise AssertionError("Continuous interval coverage failed")


def thesis_matrix(n, d, nu, ts, start, c1, c2):
    delayed = np.array([[thesis_basis(t-d, s, n, c1, c2)
                         for s in range(n)] for t in range(n)])
    rotation = np.exp(2j*np.pi*nu*ts*(start+np.arange(n)))
    return transform(n, c1, c2) @ (rotation[:, None]*delayed)


def appendix_matrix(n, d, nu, ts, start, c1, c2):
    out = np.zeros((n,n), complex)
    for r in range(n):
        for s in range(n):
            prefactor = np.exp(2j*np.pi*(c1*d*d+c2*(s*s-r*r)-s*d/n+nu*ts*start))/n
            total = 0j
            for t in range(n):
                rho = np.floor(2*c1*((t-d) % n)+s/n)
                total += np.exp(2j*np.pi*(((s-r)/n-2*c1*d+nu*ts)*t+rho*d))
            out[r,s] = prefactor*total
    return out


def grouped_matrix(n, d, nu, ts, start, c1, c2, *, output_index=False):
    """Huang-style grouping derived from the preceding continuous waveform.

    input-index/continuous-interval choice is stated explicitly: not a claim
    that the printed discrete interval formula is reproduced literally.
    output_index=True is only a sensitivity diagnostic for the printed index.
    """
    out = np.zeros((n,n), complex)
    c = round(2*n*c1)
    iota = d-np.floor(d+.5)
    source_k = -n*nu*ts  # Source uses negative Doppler exponential.
    equivalent_delay = source_k+c*d
    for r in range(n):
        for s in range(n):
            total = 0j
            for q, (lo, hi) in enumerate(intervals(n, c1, r if output_index else s)):
                subtotal = sum(np.exp(2j*np.pi*(s-r-equivalent_delay)*t/n)
                               for t in range(n) if lo <= ((t-d) % n) < hi)
                total += np.exp(2j*np.pi*q*iota)*subtotal
            out[r,s] = np.exp(2j*np.pi*(c1*d*d+c2*(s*s-r*r)-s*d/n+nu*ts*start))*total/n
    return out


def error(a, b):
    return dict(relative_frobenius=float(np.linalg.norm(a-b)/np.linalg.norm(b)),
                maximum_absolute=float(np.max(np.abs(a-b))))


def main():
    checks = []
    def check(name, a, b, **params):
        result = error(a,b)
        checks.append(dict(name=name, parameters=params, **result,
                           passed=result['relative_frobenius'] < TOLERANCE))

    cases = [(16,7/32,1/320,336), (8,3/16,1/160,168)]
    for n, c1, c2, prefix in cases:
        ts = 1/(n*30000.)
        delays = [0.,1.,n-1.,float(n),n+1.,float(prefix-1),float(prefix),
                  .05,.12345,1/7-1e-8,1/7+1e-8,n-.63,n+.37,prefix-.6]
        for d in delays:
            for nu in [0.,-41000.,13791.25,41000.]:
                args = (n,d,nu,ts,prefix,c1,c2)
                actual = continuous_path_matrix(*args)
                p = dict(n=n, delay_samples=d, doppler_hz=nu)
                check('thesis_continuous_intervals_recursive_cpp', thesis_matrix(*args), actual, **p)
                check('appendix_element_expansion', appendix_matrix(*args), actual, **p)
                check('huang_grouping_continuous_input_intervals', grouped_matrix(*args), actual, **p)
                if d.is_integer():
                    independent = full_delay_path_matrix(n,FoldedDelay.from_full(int(d),n),nu,ts,prefix,c1,c2)
                    check('integer_delay_matrix', independent,actual,**p)
                cycles = int(np.floor(d/n))
                folded = d-cycles*n
                scalar = np.exp(2j*np.pi*(2*n*c1*cycles*folded+c1*cycles**2*n**2))
                short = continuous_path_matrix(n,folded,nu,ts,prefix,c1,c2)
                check('multicycle_delay_scalar',scalar*short,actual,**p)
                beta = (2*np.pi*nu*(n+prefix)*ts+np.pi) % (2*np.pi)-np.pi
                for frame in [1,7,19]:
                    shifted = continuous_path_matrix(n,d,nu,ts,prefix+frame*(n+prefix),c1,c2)
                    check('frame_phase',np.exp(1j*frame*beta)*actual,shifted,frame=frame,**p)

    n, c1, c2, ts = cfg.N,cfg.C1,cfg.C2,1/cfg.BANDWIDTH_HZ
    rng = np.random.default_rng(20261102)
    pilot = rng.standard_normal((7,3,n))+1j*rng.standard_normal((7,3,n))
    slopes = np.array([-.1234,1.231,-2.71])
    expected = np.empty_like(pilot)
    for q in range(7):
        for k in range(3):
            expected[q,k] = pilot[q,k]*np.exp(1j*q*slopes[k])
    check('phase_operator_eq10',phase_operator(pilot,slopes),expected)
    for delay,nu in [(.12345,-41000.),(7.37,13791.25),(15.4,41000.)]:
        base = np.exp(-2j*np.pi*c1*delay**2)*continuous_path_matrix(n,delay,nu,ts,0,c1,c2)
        check('frontend_path_atom',path_atom(delay,nu/cfg.DELTA_F_HZ),base,delay=delay,nu=nu)
        expected = np.concatenate([np.exp(2j*np.pi*nu*q*(n+cfg.N_CPP)*ts)*(base@pilot[q,1]) for q in range(7)])
        check('frontend_sensed_atom',sensed_atom(pilot,1,(delay,nu/cfg.DELTA_F_HZ)),expected,delay=delay,nu=nu)

    boundary = n/7
    eps = 1e-10
    jump = thesis_basis(boundary+eps,0,n,c1,c2)/thesis_basis(boundary-eps,0,n,c1,c2)
    jump_diagnostic = dict(n=n,c1=c1,input_index=0,boundary_samples=boundary,
                           predicted_ratio=[float(np.cos(-2*np.pi*boundary)),float(np.sin(-2*np.pi*boundary))],
                           observed_ratio=[float(jump.real),float(jump.imag)],
                           amplitude_jump_relative=float(abs(jump-1)))
    matrix_jumps = []
    for eps in [1e-4,1e-6,1e-8,1e-10]:
        left = continuous_path_matrix(n,1/7-eps,0,ts,cfg.N_CPP,c1,c2)
        right = continuous_path_matrix(n,1/7+eps,0,ts,cfg.N_CPP,c1,c2)
        matrix_jumps.append(dict(epsilon=eps,**error(right,left)))
    args = (n,.12345,13791.25,ts,cfg.N_CPP,c1,c2)
    index_diagnostic = error(grouped_matrix(*args,output_index=True),continuous_path_matrix(*args))

    baseline = json.loads((HERE/'BASELINE.json').read_text(encoding='utf-8-sig'))
    changed = [path for path,digest in baseline.items()
               if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest]
    names = sorted({r['name'] for r in checks})
    summary = {name:dict(count=sum(r['name']==name for r in checks),
                         maximum_relative_frobenius=max(r['relative_frobenius'] for r in checks if r['name']==name),
                         passed=all(r['passed'] for r in checks if r['name']==name)) for name in names}
    results = dict(scope='Deterministic identities within the declared point-sampled analytic model; no pulse-shaped transmitter/receiver validation.',
                   tolerance=TOLERANCE,number_of_checks=len(checks),summary=summary,
                   all_identity_checks_passed=all(r['passed'] for r in checks),
                   waveform_jump=jump_diagnostic,channel_matrix_jump=matrix_jumps,
                   printed_output_index_sensitivity=dict(note='Continuous intervals retained; only input/output index switched. Not an author-code reproduction.',**index_diagnostic),
                   protected_baseline=dict(number_of_files=len(baseline),changed=changed),
                   checks=checks)
    (HERE/'NUMERICAL_CHECKS.json').write_text(json.dumps(results,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in results.items() if k != 'checks'},ensure_ascii=False,indent=2))
    if changed or not results['all_identity_checks_passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
