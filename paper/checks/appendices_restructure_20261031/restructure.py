"""Move the authorized appendix material into its corresponding body sections."""
from pathlib import Path
import hashlib
import json

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]
base = json.loads((RUN/'BASELINE.json').read_text(encoding='utf-8'))
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
for rel, digest in base['files'].items():
    assert sha(PAPER/rel) == digest, ('source changed since snapshot', rel)

read = lambda rel: (RUN/'before'/rel).read_text(encoding='utf-8')
changes = {}
def replace_once(text, old, new):
    assert text.count(old) == 1, ('replacement match count', text.count(old), old)
    return text.replace(old, new, 1)

afile = 'sections/appendix_parameter_estimation.tex'
bfile = 'sections/appendix_afdm_channel_model.tex'
dfile = 'sections/appendix_implementation.tex'
a, b, d = read(afile), read(bfile), read(dfile)

# A: keep the optional phase estimator; move the complete noise estimator to V-A1.
phase, noise = a.split(r'\subsection{Noise variance estimation}')
phase = replace_once(phase, r'\section{Phase and Noise Estimation}', r'\section{Inter-Frame Phase Estimation}')
phase = replace_once(phase, r'\subsection{Inter-frame phase estimation}'+'\n', '')
phase = replace_once(phase, r'Stack $[\mathbf Y_{\rm s}]',
    'When inter-frame phases are unavailable, estimate them as follows.\n'
    r'Stack $[\mathbf Y_{\rm s}]')
changes[afile] = phase.rstrip()+'\n'

# B: the waveform definition belongs in the system model. The path operator is
# already given there; retain the entrywise and integer-delay derivations here.
wave_start = b.index('To specify the waveform')
wave_end = b.index('For normalized delay')
waveform = b[wave_start:wave_end].rstrip()
entry_start = b.index('\\begin{equation}', b.index('Substituting the basis'))
changes[bfile] = (
    '\\section{Fractional-Delay AFDM Channel Matrix}\n'
    '\\label{app:afdm-model}\n\n'
    'Substituting the basis waveform in \\eqref{eq:continuous-waveform}\n'
    'into \\eqref{eq:path-operator-system} gives\n'
    + b[entry_start:].replace(r'\eqref{eq:path-operator}', r'\eqref{eq:path-operator-system}')
)
rel = 'sections/02_system_model.tex'
s = read(rel)
anchor = 'After CPP removal and DAFT demodulation, the effective channel of'
s = replace_once(s, anchor, waveform+'\n\n'+anchor)
s = replace_once(s,
    'The CPP-extended basis $\\varphi_n$ is defined in\n'
    'Appendix~\\ref{app:afdm-model}; frame $0$ starts at $g=N_{\\rm CPP}$.',
    'Frame $0$ starts at $g=N_{\\rm CPP}$. Appendix~\\ref{app:afdm-model}\n'
    'derives the entries of this matrix and its integer-delay form.')
changes[rel] = s

# D: split computational formulas, network inputs, algorithmic stopping rules,
# and experimental parameter values; reuse their mathematical content verbatim.
linear = d.split(r'\subsection{Linear Update Implementation}')[1].split(r'\subsection{Network Inputs and Training Settings}')[0].strip()
network = d.split(r'\subsection{Network Inputs and Training Settings}')[1].split(r'\subsection{Stopping Criteria}')[0].strip()
normalization, classifier, derivative = network.split('\n\n')
stopping = d.split(r'\subsection{Stopping Criteria}')[1].strip()
stop_rule, stop_values = stopping.rsplit('\n\n', 1)

rel = 'sections/03_bayesian_receiver_design.tex'
s = read(rel)
linear = linear.replace('can be evaluated using a thin SVD',
    'can be evaluated using a thin singular value decomposition (SVD)')
s = replace_once(s,
    'A thin singular value decomposition (SVD) of $\\widehat{\\mathbf A}$\n'
    'can be reused throughout the block to evaluate these quantities;\n'
    'the equivalent expressions are given in Appendix~\\ref{app:implementation}.',
    linear)
changes[rel] = s

rel = 'sections/04_generative_priors.tex'
s = read(rel)
s = replace_once(s, 'network; numerical settings appear in Appendix~\\ref{app:implementation}.',
    'network; numerical settings appear in Section~\\ref{sec:receiver-settings}.')
s = replace_once(s,
    'random initialization using \\eqref{eq:classifier-loss}. It combines\n'
    'maps of $R$ and $F_\\theta(R,v\\I_D)$ with variance, energy, and\n'
    'inner-product features (Appendix~\\ref{app:implementation}).',
    'random initialization using \\eqref{eq:classifier-loss}.\n'+classifier)
changes[rel] = s

rel = 'sections/05_overall_algorithm.tex'
s = read(rel)
s = replace_once(s,
    '\\label{sec:schedule}\n\\label{sec:frontend}\n\\label{sec:damping}\n\n'
    'Form $\\widehat{\\mathbf A}$ from the available inter-frame phases\n'
    'via \\eqref{eq:effective-pilot}. Estimate missing phases\n'
    'by variable projection \\cite{oleary2013}, and estimate the physical\n'
    'noise variance $\\widehat\\sigma^2$ by minimum description length\n'
    '\\cite{nadakuditi2008}, as detailed in Appendix~\\ref{app:frontend}.\n'
    'Both remain fixed within the block.',
    '\\label{sec:schedule}\n\n'
    '\\subsubsection{Phase and Noise Estimation}\n'
    '\\label{sec:frontend}\n'
    'Form $\\widehat{\\mathbf A}$ from the available inter-frame phases\n'
    'via \\eqref{eq:effective-pilot}. When these phases are unavailable,\n'
    'estimate them by variable projection \\cite{oleary2013}, as detailed\n'
    'in Appendix~\\ref{app:frontend}.\n\n'
    'For the physical noise variance, use the following observation-based estimate.\n'
    + noise.strip()+'\n\n'
    '\\subsubsection{Message Updates}\n\\label{sec:damping}')
s = replace_once(s, 'SVD implementation in Appendix~\\ref{app:implementation}. For',
    'SVD expression in \\eqref{eq:linear-fraction}. For')
s = replace_once(s, 'Appendix~\\ref{app:implementation} and update the stopping history;',
    'Section~\\ref{sec:stopping-criteria} and update the stopping history;')
s = replace_once(s,
    'Stopping checks and numerical settings are specified in\n'
    'Appendix~\\ref{app:implementation}.',
    '\\subsubsection{Stopping Criteria}\n\\label{sec:stopping-criteria}\n\n'
    +stop_rule+'\n\n'
    'The numerical settings are given in Section~\\ref{sec:receiver-settings}.')
changes[rel] = s

rel = 'sections/06_simulation_results.tex'
s = read(rel)
s = replace_once(s,
    'All use the same fixed normalization. The denoiser uses Adam,',
    'All use the same fixed normalization scale $s=0.2647966453$.\n'
    'The denoiser uses Adam,')
s = replace_once(s,
    'the same covariance form. Appendix~\\ref{app:implementation} gives\n'
    'the normalization scale and selected checkpoints.',
    'the same covariance form. The selected checkpoints are epoch $200$\n'
    'for the denoiser and epoch $90$ for the classifier.')
s = replace_once(s, r'\subsubsection{Compared Receivers}',
    '\\subsubsection{Compared Receivers}\n\\label{sec:receiver-settings}')
s = replace_once(s,
    'noise estimates. STMP and GP-CCD-MP-DRE use activity threshold $0.5$,\n'
    '$60$--$600$ iterations, relative-change tolerance $5\\times10^{-4}$,\n'
    'and activity/message-stability checks (Appendix~\\ref{app:implementation}).\n'
    'Their default new-message weights are $0.2$ and $0.4$.',
    'noise estimates. STMP and GP-CCD-MP-DRE use activity threshold $0.5$\n'
    'and the stopping checks in Section~\\ref{sec:stopping-criteria}.\n'
    +stop_values+'\n'
    'Their default new-message weights are $0.2$ and $0.4$.\n\n'
    +derivative+'\n')
changes[rel] = s

changes['main.tex'] = replace_once(read('main.tex'),
    '\\input{sections/appendix_implementation}\n', '')

# All expected edits have matched before any manuscript file is written.
for rel, s in changes.items():
    (PAPER/rel).write_text(s, encoding='utf-8')
assert (RUN/'before'/dfile).read_bytes() == (PAPER/dfile).read_bytes()
(PAPER/dfile).unlink()
assert sha(PAPER/'sections/appendix_evaluation_protocol.tex') == base['files']['sections/appendix_evaluation_protocol.tex']
assert sha(PAPER/'sections/01_introduction.tex') == base['files']['sections/01_introduction.tex']

mapping = {
    'A_phase': 'Retained as appendix A; optional when inter-frame phases are unavailable.',
    'A_noise': 'Moved in full to V-A1, Phase and Noise Estimation.',
    'B_waveform': 'Moved to II-B before the effective-channel tensor.',
    'B_path_operator': 'Duplicate appendix equation merged with existing eq:path-operator-system; references redirected.',
    'B_derivation': 'Entrywise expansion, integer-delay reduction and inter-frame relation retained as appendix B.',
    'C': 'Byte-identical; remains appendix C.',
    'D_linear': 'Moved to III-B, Multi-Frame Linear Estimation.',
    'D_network_inputs': 'Moved to IV-D, Offline Training.',
    'D_training_values': 'Moved to VI-A1, Channel Samples and Training.',
    'D_derivative_values': 'Moved to VI-A2, Compared Receivers.',
    'D_stopping_rules': 'Moved to V-A3, Stopping Criteria.',
    'D_stopping_values': 'Moved to VI-A2, Compared Receivers.',
    'D_file': 'Removed from active sources after archiving in before/sections/; all content moved or deduplicated.'
}
(RUN/'CONTENT_MAP.json').write_text(json.dumps(mapping,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'modified':list(changes),'retired':dfile,'C_unchanged':True,'introduction_unchanged':True},ensure_ascii=False))
