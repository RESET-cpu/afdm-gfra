"""Authorized notation cleanup. No experiment code, data, or settings changed."""
from pathlib import Path
import re, json, hashlib, shutil

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
SECTIONS = PAPER / 'sections'
files = [PAPER/'main.tex', PAPER/'main_full.tex', PAPER/'references.bib',
         PAPER/'main.pdf', PAPER/'main_full.pdf', PAPER/'main.aux',
         *SECTIONS.glob('*.tex'), *PAPER.glob('figures/*')]
manifest = {}
for p in files:
    if not p.is_file(): continue
    rel = p.relative_to(PAPER)
    dest = RUN/'before'/rel
    if dest.exists():
        assert dest.read_bytes() == p.read_bytes(), 'Do not rerun after edits'
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dest)
    manifest[str(rel)] = hashlib.sha256(p.read_bytes()).hexdigest()
(RUN/'BEFORE.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

def replace(text, old, new):
    assert old in text, old[:130]
    return text.replace(old, new)

# First apply common object notation only in sections that use those objects.
names = ['02_system_model', '03_bayesian_receiver_design', '04_generative_priors',
         '05_overall_algorithm', '06_simulation_results',
         'appendix_parameter_estimation', 'appendix_afdm_channel_model',
         'appendix_evaluation_protocol']
texts = {}
for name in names:
    t = (SECTIONS/(name+'.tex')).read_text(encoding='utf-8')
    # Plain capitals were tensor-valued objects; they become device matrices.
    for x in ['H','X','R','E','F']:
        def bold_plain(m):
            prefix = t[:m.start()]
            if re.search(r'\\(?:mathbf|mathsf|mathbb|mathrm|rm)\s*\{?$', prefix):
                return x
            if re.search(r'_\{?$', prefix):
                return x  # descriptive subscripts such as P_H and C_{X,k}
            return r'\mathbf '+x
        t = re.sub(r'(?<![A-Za-z\\])'+x+r'(?![A-Za-z])', bold_plain, t)
    # Existing explicitly typeset objects must not acquire a second command.
    t = t.replace(r'\mathbf \mathbf ', r'\mathbf ')
    t = t.replace(r'\widehat X', r'\widehat{\mathbf X}')
    t = t.replace(r'\widehat\mathbf X', r'\widehat{\mathbf X}')
    t = t.replace(r'\mu_k', r'\mathbf H_k^{\rm post}')
    t = t.replace(r'c_k', r'\tau_k^{\rm ext}')
    t = t.replace(r'\tau_c', r'\tau_{\rm c}')
    t = t.replace(r'P_{qkn}', r'[\mathbf p_{qk}]_n')
    t = t.replace(r'S_\theta', r'\mathbf s_\theta')
    t = t.replace(r'f_\theta', r'\mathbf f_\theta')
    t = t.replace(r'g_\theta', r'\mathbf g_\theta')
    texts[name] = t

t = texts['02_system_model']
start = t.index('Let $[\\mathbf p_{qk}]_n')
end = t.index('\nWe impose the condition', start)
t = t[:start] + r'''Let $\mathbf p_{qk}\in\mathbb C^N$ denote the pilot vector transmitted by
device $k$ in frame $q$, where $k=1,\ldots,K$ and $q=0,\ldots,Q-1$.
Its $n$th entry $[\mathbf p_{qk}]_n$ is the symbol on chirp subcarrier $n$.
The pilot symbols are known at the satellite receiver.
Define $\mathbf P_k=[\mathbf p_{0k},\ldots,\mathbf p_{Q-1,k}]^{\mathsf T}$
and $\mathbf P=[\mathbf P_1,\ldots,\mathbf P_K]\in\mathbb C^{Q\times KN}$,
where $(\cdot)^{\mathsf T}$ denotes transpose.
''' + t[end:]
start = t.index('Denote by $')
end = t.index('For a path with gain', start)
t = t[:start] + r'''After CPP removal and DAFT demodulation, the reference-frame channel
from device $k$ to antenna $m$ is the matrix
\begin{equation}
 \mathbf H_{k,m}
 =[\mathbf a_k]_m\sum_{\ell=1}^{L_k}g_{k\ell}
 \mathbf G(\tau_{k\ell}/T_s,\nu_k;N_{\rm CPP}),
 \label{eq:channel}
\end{equation}
whose row and column indices correspond to received and transmitted
symbols, respectively, with $m=0,\ldots,M-1$.
We collect the antenna channels in the device matrix
$\mathbf H_k=[\mathbf H_{k,0}^{\mathsf T},\ldots,
\mathbf H_{k,M-1}^{\mathsf T}]\in\mathbb C^{N\times MN}$.
''' + t[end:]
t = replace(t, r''' \beta_k=2\pi\!\left(\nu_kT_{\rm frame}
 -\left\lfloor\nu_kT_{\rm frame}+\frac12\right\rfloor\right),''',
 r''' \beta_k\equiv2\pi\nu_kT_{\rm frame}\pmod{2\pi},''')
t = replace(t, r''' A_{qkn}=[\mathbf p_{qk}]_ne^{\mathrm jq\beta_k}.''',
 r''' \mathbf A_k=\diag\{e^{\mathrm jq\beta_k}\}_{q=0}^{Q-1}\mathbf P_k,
 \qquad \mathbf A=[\mathbf A_1,\ldots,\mathbf A_K].''')
start = t.index('After removing the CPP and applying the DAFT, the received signal')
end = t.index('Since the $Q$ frames', start)
t = t[:start] + r'''Let $\mathbf Y_q\in\mathbb C^{M\times N}$ collect the received symbols
in frame $q$ after CPP removal and DAFT demodulation, and let
$\mathbf W_q$ contain the corresponding independent $\CN(0,\sigma^2)$ noise entries.
Stack the frame observations as
$\mathbf Y=[\vect(\mathbf Y_0^{\mathsf T}),\ldots,
\vect(\mathbf Y_{Q-1}^{\mathsf T})]^{\mathsf T}$, and form $\mathbf W$ in the same way.
With $\mathbf X=[\mathbf X_1^{\mathsf T},\ldots,
\mathbf X_K^{\mathsf T}]^{\mathsf T}$, the received signal is
\begin{equation}
 \mathbf Y=\sum_{k=1}^K\mathbf A_k\mathbf X_k+\mathbf W
 =\mathbf A\mathbf X+\mathbf W,
 \label{eq:mmv}
\end{equation}
where $\mathbf Y,\mathbf W\in\mathbb C^{Q\times MN}$,
$\mathbf A\in\mathbb C^{Q\times KN}$, and
$\mathbf X\in\mathbb C^{KN\times MN}$.
This block formulation follows \cite[Sec.~II-A]{cai2026}, with the
device matrices defined by the AFDM channel in \eqref{eq:channel}.
''' + t[end:]
start = t.index('The MMSE estimate of')
t = t[:start] + r'''The inference targets are the MMSE channel estimate
$\E_q[\mathbf X_k\mid\mathbf Y]$ and the posterior activity probability
$q(\alpha_k=1\mid\mathbf Y)$.
'''
texts['02_system_model'] = t

t = texts['03_bayesian_receiver_design']
t = t.replace('We rearrange $\\mathbf R_{\\rm L}$ by device and pass the resulting tensors',
              'We partition $\\mathbf R_{\\rm L}$ by device and pass the resulting matrix blocks')
start = t.index('For the channel tensor')
end = t.index('This Gaussian input message', start)
t = t[:start] + r'''The operator $\vect(\cdot)$ stacks matrix columns; for $\mathbf H_k$,
the transmitted-symbol index varies fastest, followed by the
received-symbol and antenna indices.
''' + t[end:]
start = t.index('Combining its likelihood')
end = t.index('\n\\subsubsection{Activity Detection}', start)
t = t[:start] + r'''Combining its likelihood with the channel prior gives the conditional moments
\begin{equation}
 \begin{aligned}
 \mathbf H_k^{\rm post}&\approx
 \E[\mathbf H_k\mid\mathbf R_k,\alpha_k=1],\\
 t_k&\approx\frac1D\tr\operatorname{Cov}
 (\vect(\mathbf H_k)\mid\mathbf R_k,\alpha_k=1).
 \end{aligned}
 \label{eq:conditional-channel-integrals}
\end{equation}
The approximations are evaluated under the local model
\eqref{eq:pseudo-awgn}; Section~\ref{sec:schedule} specifies their computation.
''' + t[end:]
t = replace(t,
 r'q_{1,v}(\mathbf R)&=\int\CN(\vect(\mathbf R);\vect(\mathbf H),v\I_D)q_{\rm tr}(dH),',
 r'q_{1,v}(\mathbf R)&=\E_{\mathbf H\sim q_{\rm tr}}[\CN(\vect(\mathbf R);\vect(\mathbf H),v\I_D)],')
start = t.index('and covariance $t_k')
end = t.index('\nTo compute the posterior covariance', start)
t = t[:start] + r'''and covariance $t_k\I_D$ gives a Bernoulli--Gaussian approximation
\cite[Secs.~III-C--III-D]{liu2018}, \cite[Sec.~III-B]{cai2026}.
It assigns probability $1-p_k$ to the zero matrix and probability $p_k$
to this Gaussian component. Its mean is
\begin{equation}
 \widehat{\mathbf X}_k=p_k\mathbf H_k^{\rm post}.
 \label{eq:mixture}
\end{equation}
''' + t[end:]
texts['03_bayesian_receiver_design'] = t

t = texts['04_generative_priors']
t = t.replace('the conditional mean in \\eqref{eq:conditional-channel-integrals}',
              'the exact conditional mean underlying \\eqref{eq:conditional-channel-integrals}')
t = t.replace(r'$\Pr(a=1)=\pi_{\rm tr}=1/2$', r'$\Pr(a=1)=1/2$')
t = t.replace(r'z^\star(\mathbf R,v)=\logit\pi_{\rm tr}', r'z^\star(\mathbf R,v)=')
t = t.replace(r'       +\log\frac{q_{1,v}(\mathbf R)}{q_{0,v}(\mathbf R)}.',
              r'       \log\frac{q_{1,v}(\mathbf R)}{q_{0,v}(\mathbf R)}.')
t = replace(t, r'''We estimate the log density ratio by subtracting $\logit\pi_{\rm tr}$ from
the classifier output \cite[Sec.~4.2]{menon2016}.''',
 r'''With balanced training classes, the classifier output directly estimates
the log density ratio \cite[Sec.~4.2]{menon2016}.''')
t = t.replace(r'-\logit\pi_{\rm tr}', '')
t = t.replace('complex-valued denoiser $', 'complex-valued matrix denoiser $')
texts['04_generative_priors'] = t

t = texts['05_overall_algorithm']
t = replace(t, r''' \tau_{\rm raw}=\frac1K\sum_{k=1}^K\widehat\tau_k,\qquad
 \tau^{\rm post}=\max\{\tau_{\rm raw},\tau_{\min}\}.''',
 r''' \tau^{\rm post}=\max\left\{\frac1K\sum_{k=1}^K\widehat\tau_k,
 \tau_{\min}\right\}.''')
t = t.replace(r'$\mathbf E_k=0$', r'$\mathbf E_k=\mathbf0$')
t = t.replace(r'pilot symbols $\{[\mathbf p_{qk}]_n\}$', r'pilot vectors $\{\mathbf p_{qk}\}$')
t = replace(t, 'initialize as above\n and normalize as in Section~\\ref{sec:frontend}.',
            'normalize as in Section~\\ref{sec:frontend}\n and initialize as above.')
t = t.replace(r'\item Otherwise, retain the sites',
              r'\item If $v$ is outside the training interval, retain the sites')
t = replace(t, r'$\mathbf y_{qr}=(Y_{q0r},\ldots,Y_{q,M-1,r})^{\mathsf T}$',
              r'$\mathbf y_{qr}$ be column $r$ of $\mathbf Y_q$')
# Precedence must be explicit for a superscripted variance.
t = t.replace(r'\tau_k^{\rm ext}=((\tau^{\rm post})^{-1}-v^{-1})^{-1}',
              r'\tau_k^{\rm ext}=((\tau^{\rm post})^{-1}-v^{-1})^{-1}')
texts['05_overall_algorithm'] = t

t = texts['06_simulation_results']
t = t.replace(r'\mathbf Y_0=\mathbf A\mathbf X', r'\mathbf Y_{\rm sig}=\mathbf A\mathbf X')
t = t.replace(r'\norm{\mathbf Y_0}_F', r'\norm{\mathbf Y_{\rm sig}}_F')
# Define the inverse reshape at the actual neural-network boundary.
needle = 'The denoiser'
idx = t.find(needle, t.index(r'\label{sec:network-settings}'))
assert idx >= 0
t = t[:idx] + r'''Device matrices are reshaped to $M\times N\times N$ arrays for the
networks, preserving the antenna--output--input order of $\vect(\mathbf H_k)$.
''' + t[idx:]
texts['06_simulation_results'] = t

t = texts['appendix_parameter_estimation']
t = replace(t, r'''Stack $[\mathbf Y_{\rm s}]_{qN+r,m}=Y_{qmr}$ into
$\mathbf Y_{\rm s}\in\mathbb C^{QN\times M}$.''',
 r'''Stack the transposed frame observations as
$\mathbf Y_{\rm s}=[\mathbf Y_0,\ldots,\mathbf Y_{Q-1}]^{\mathsf T}
\in\mathbb C^{QN\times M}$.''')
# Use the already defined matrix-vector product instead of a second scalar expansion.
t = t.replace(r'\sum_{n=0}^{N-1}[\mathbf G_0(d,\nu)]_{rn}[\mathbf p_{qk}]_n.',
              r'[\mathbf G_0(d,\nu)\mathbf p_{qk}]_r.')
texts['appendix_parameter_estimation'] = t
t = texts['appendix_afdm_channel_model'].replace('the effective tensor satisfies', 'the device matrix satisfies')
t = t.replace(' G_{rn}', r' [\mathbf G(d,\nu;g)]_{rn}')
texts['appendix_afdm_channel_model'] = t
t = texts['appendix_evaluation_protocol']
t = t.replace(r'\tau_k^{\rm ext}^{-1}', r'(\tau_k^{\rm ext})^{-1}')
texts['appendix_evaluation_protocol'] = t

for name, text in texts.items():
    # Accidental bolding of the R used to denote the real field is not allowed.
    text = text.replace(r'\mathbb \mathbf R', r'\mathbb R')
    assert r'\mathbf \mathbf' not in text
    (SECTIONS/(name+'.tex')).write_text(text, encoding='utf-8', newline='\n')

t = (PAPER/'main.tex').read_text(encoding='utf-8')
t = replace(t, r'\noindent\textit{Notation:} ',
 r'\noindent\textit{Notation:} Bold lowercase and uppercase letters denote vectors and matrices, respectively. ')
(PAPER/'main.tex').write_text(t, encoding='utf-8', newline='\n')
print('Backed up', len(manifest), 'files; revised eight sections and notation sentence.')
