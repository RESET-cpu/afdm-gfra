"""Deterministic algebra and source checks; no receiver training or performance test."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT.parent
rng = np.random.default_rng(20261021)
errors = {}

def close(name, left, right, tolerance=1e-10):
    error = float(np.max(np.abs(np.asarray(left) - np.asarray(right))))
    scale = max(1., float(np.max(np.abs(right))))
    errors[name] = max(errors.get(name, 0.), error / scale)
    assert error <= tolerance * scale, (name, error, scale)

def complex_array(shape):
    return rng.normal(size=shape) + 1j * rng.normal(size=shape)

for Q, J, rank in [(4, 9, 4), (9, 4, 4), (4, 9, 2)]:
    A = complex_array((Q, rank)) @ complex_array((rank, J))
    Y, M, X = (complex_array((Q, 3)), complex_array((J, 3)),
               complex_array((J, 3)))
    U, s, Vh = np.linalg.svd(A, full_matrices=False)
    for w, noise in [(0.2, 0.7), (2., .01), (.0001, 2.)]:
        cov = np.linalg.inv(np.eye(J)/w + A.conj().T @ A/noise)
        correction = w*A.conj().T @ np.linalg.solve(
            noise*np.eye(Q)+w*A@A.conj().T, Y-A@M)
        gain = w*s/(noise+w*s*s)
        svd_correction = Vh.conj().T @ (gain[:, None]*(U.conj().T@(Y-A@M)))
        close("svd_correction", svd_correction, correction)
        f = ((J-len(s)) + np.sum(noise/(noise+w*s*s)))/J
        d = np.sum(w*s*s/(noise+w*s*s))/J
        close("trace_fraction", f, np.trace(cov).real/J/w)
        close("complementary_fractions", f+d, 1.)
        v0 = w*f/d
        close("gaussian_query", M+correction/d,
              v0*((M+correction)/(w*f)-M/w))
        W = Y-A@X
        L = w*A.conj().T @ np.linalg.inv(noise*np.eye(Q)+w*A@A.conj().T)/d
        close("query_error", M+correction/d-X, (L@A-np.eye(J))@(X-M)+L@W)
        for gamma in [.3, 1., 2.]:
            xi = gamma*f/d
            v = w*xi
            R = M+(1+xi)*correction
            t = np.trace(cov).real/J
            compact_v = gamma*w*t/(w-t)
            close("compact_query_variance", compact_v, v)
            close("compact_query_mean", M+(1+compact_v/w)*correction, R)
            t_cal = w*v/(w+v)
            close("calibrated_mean", R, v*((M+correction)/t_cal-M/w))
            estimate = complex_array((J, 3))
            residual = Y-A@estimate
            E = X-estimate
            close("residual_expansion", np.linalg.norm(residual)**2-Q*3*noise,
                  np.linalg.norm(A@E)**2+np.linalg.norm(W)**2-Q*3*noise
                  +2*np.vdot(A@E,W).real)
            Areal = np.block([[A.real,-A.imag],[A.imag,A.real]])
            close("real_operator_energy", np.linalg.norm(Areal)**2, 2*np.linalg.norm(A)**2)
            for raw in [-3*v, 0., 2*v]:
                positive = np.exp(.2)*(.02*v*np.logaddexp(0.,raw/(.02*v))+1e-6)
                ratio = 1e-6+(.95-1e-6)*np.tanh(positive/((.95-1e-6)*v))
                assert 0 < ratio <= .95
                tau = v*ratio
                proposal = (estimate-ratio*R)/(1-ratio)
                wp = tau/(1-ratio)
                close("feedback_division", proposal, wp*(estimate/tau-R/v))
                delta = min(1., .2/wp)
                wn = 1/((1-delta)/w+delta/wp)
                mn = wn*((1-delta)*M/w+delta*proposal/wp)
                assert wn > 0 and np.isfinite(mn).all()
                close("damped_natural_parameter", mn/wn, (1-delta)*M/w+delta*proposal/wp)

pi, kappa = .3, 1.7
h = np.array([[1.,2.],[-.5,3.],[2.,-.4]])
probs = np.array([.2,.5,.3])
mean = probs@h
conditional_var = np.sum(probs*np.sum((h-mean)**2,axis=1))
entropy = -pi*np.log(pi)-(1-pi)*np.log(1-pi)
for p in [.1,.3,.8]:
    for mu in [mean, np.array([3.,-1.])]:
        lhs = pi/kappa*np.sum(probs*np.sum((h-mu)**2,axis=1))-pi*np.log(p)-(1-pi)*np.log(1-p)
        kl = pi*np.log(pi/p)+(1-pi)*np.log((1-pi)/(1-p))
        rhs = pi/kappa*conditional_var+entropy+pi/kappa*np.sum((mu-mean)**2)+kl
        close("conditional_risk", lhs, rhs)

counts = np.array([2,5,8])
channel_sums, bce_sums = np.array([3.,7.,2.]), np.array([.5,1.,4.])
energy = 41.
close("scene_channel_normalization", np.mean(channel_sums/(energy/3)),sum(channel_sums)/energy)
close("scene_bce_normalization", np.mean(bce_sums/(sum(counts)/3)),sum(bce_sums)/sum(counts))

manifest = json.loads((PAPER/"DCN/COPY_MANIFEST.json").read_text(encoding="utf-8-sig"))
for row in manifest["files"]:
    for base in [PAPER, PAPER/"DCN"]:
        path = base / row["path"].replace("\\", "/")
        assert hashlib.sha256(path.read_bytes()).hexdigest().upper() == row["sha256"], path

main = (ROOT/"main.tex").read_text(encoding="utf-8-sig")
strip_comments = lambda s: re.sub(r"(?<!\\)%.*", "", s)
inputs = re.findall(r"\\input\{([^}]+)\}",strip_comments(main))
source = strip_comments(main) + "\n" + "\n".join(
    strip_comments((ROOT/(name+".tex")).read_text(encoding="utf-8-sig")) for name in inputs)
labels = re.findall(r"\\label\{([^}]+)\}", source)
assert len(labels) == len(set(labels)), "Duplicate labels"
refs = re.findall(r"\\(?:eqref|ref)\{([^}]+)\}",source)
assert not set(refs)-set(labels), set(refs)-set(labels)
bib = (ROOT/"references.bib").read_text(encoding="utf-8-sig")
keys = set(re.findall(r"@\w+\{([^,\s]+)",bib))
cited = {key.strip() for item in re.findall(r"\\cite(?:\[[^\]]*\])?\{([^}]+)\}",source)
         for key in item.split(",")}
assert not cited-keys, cited-keys
assert not re.search(r"500 independent|Two score networks|separately trained classifier",source)
report = dict(status="PASS", scope="Deterministic synthetic algebra and manuscript source validation; no receiver performance claim",
              relative_errors=errors, source_inputs=len(inputs), labels=len(labels),
              cited_keys=len(cited), preserved_files=len(manifest["files"]),
              compiler_status="BLOCKED: default Tectonic bundle unavailable over HTTPS",
              pdf_visual_qa="NOT_PERFORMED")
(ROOT/"checks/VALIDATION.json").write_text(json.dumps(report,indent=2)+"\n", encoding="utf-8")
print(json.dumps(report,indent=2))
