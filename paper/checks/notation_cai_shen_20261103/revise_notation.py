"""Historical staged edit helper; no inference or training.

This was used alongside manual edits, not as a complete replay script.
CHANGES.diff records the final revision; do not rerun on revised sources.
"""
from pathlib import Path
import re
import sys

RUN = Path(__file__).resolve().parent
PAPER = RUN.parents[1]

def edit(name, transform):
    path = PAPER / 'sections' / name
    raw = path.read_bytes()
    text = raw.decode('utf-8').replace('\r\n', '\n')
    revised = transform(text)
    assert revised != text, name
    path.write_text(revised, encoding='utf-8', newline='\r\n' if b'\r\n' in raw else '\n')

def replace_once(text, old, new):
    assert text.count(old) == 1, (old, text.count(old))
    return text.replace(old, new)

def covariance(text):
    # Only learning/algorithm/simulation sections, where bare C is the
    # perturbation covariance. C_{X,k} and cost subscripts are excluded.
    # Bare C denotes covariance only inside math; channel-profile C in prose
    # and the complex number field must remain untouched.
    text = re.sub(r'\$[^$]*\$|\\begin\{equation\}.*?\\end\{equation\}',
                  lambda match: re.sub(r'(?<!\\mathbb )(?<![A-Za-z\\])C(?![A-Za-z_])',
                                       lambda _: r'\mathbf C', match.group()),
                  text, flags=re.S)
    for label in ('a', 'c'):
        text = text.replace('R_{\\rm '+label+'}', '\\mathbf R_{\\rm '+label+'}')
    return text

def learning(text):
    text = covariance(text)
    return re.sub(r'\\delta(?![A-Za-z_])', lambda _: r'\delta_{\rm FD}', text)

def algorithm(text):
    text = covariance(text)
    text = text.replace(r'\tau^{-1}', r'(\tau^{\rm post})^{-1}')
    text = re.sub(r'\\tau(?![A-Za-z_^])', lambda _: r'\tau^{\rm post}', text)
    text = replace_once(text, r'U\diag(s_i)\mathbf V^{\mathsf H}',
                        r'U\diag(s_1,\ldots,s_Q)\mathbf V^{\mathsf H}')
    text = replace_once(text, 'can be reused across iterations.\nWith this decomposition,',
                        'can be reused across iterations for $Q\\leq KN$. Here\n'
                        '$s_1,\\ldots,s_Q$ are the singular values. With this decomposition,')
    text = text.replace(r'\sum_i', r'\sum_{a=1}^{Q}').replace('s_i^2', 's_a^2')
    return text

def simulation(text):
    text = covariance(text)
    text = replace_once(text, 'and independent factors\n',
                        'and independent factors of the form\n')
    text = replace_once(text,
        r'R=(1-\xi)\I_{16}'+'\n'+r'   +\xi\frac{16GG^{\mathsf H}}{\tr(GG^{\mathsf H})},',
        r'\mathbf R_{\rm corr}=(1-\xi_{\rm corr})\I_{16}'+'\n'+
        r'   +\xi_{\rm corr}\frac{16\mathbf Z_{\rm tr}\mathbf Z_{\rm tr}^{\mathsf H}}'+
        r'{\tr(\mathbf Z_{\rm tr}\mathbf Z_{\rm tr}^{\mathsf H})},')
    text = replace_once(text, r'where $G\in\mathbb C^{16\times4}$ has independent $\CN(0,1)$',
                        r'where $\mathbf Z_{\rm tr}\in\mathbb C^{16\times4}$ has independent $\CN(0,1)$')
    text = text.replace(r'entries and $\xi$ is uniform', r'entries and $\xi_{\rm corr}$ is uniform')
    text = re.sub(r'\\delta(?![A-Za-z_])', lambda _: r'\delta_{\rm FD}', text)
    text = re.sub(r'\\zeta(?![A-Za-z_])', lambda _: r'\zeta_{\rm hist}', text)
    text = replace_once(text,
        'For channel estimation, we report the normalized mean-squared error\n'
        '(NMSE) by pooling error and channel energies over the evaluated scenes:',
        'Let $\\mathcal T$ denote the set of evaluated scene indices at a given\n'
        'experimental condition, with $e\\in\\mathcal T$. For channel estimation,\n'
        'we report the normalized mean-squared error (NMSE) by pooling error\n'
        'and channel energies over these scenes:')
    text = text.replace(r'\sum_{i\in\mathcal T}', r'\sum_{e\in\mathcal T}')
    for token in ('X', 'H', r'\alpha'):
        text = text.replace(token+'_{ik}', token+'_{ek}')
    text = replace_once(text,
        r'estimate $P_{\rm tr}R/(P_{\rm tr}+v)$, where $P_{\rm tr}$ is the'+'\n'+
        'normalized training-channel power; and genie-aided conditional MMSE.',
        r'estimate $\widehat P_H R/(\widehat P_H+v)$, using the training-channel'+'\n'+
        r'power defined in Section~\ref{sec:schedule}; and genie-aided conditional MMSE.')
    return text

def frontend(text):
    text = text.replace(r'\mathbf h_k', r'\mathbf h_k^{\rm p}')
    text = text.replace(r'\mathbf h_j', r'\mathbf h_j^{\rm p}')
    text = replace_once(text, 'Search $d\\in[0,N)$ and $|\\nu|\\leq\\nu_{\\max}$. Since',
        'Here $\\mathbf h_k^{\\rm p}(d,\\nu)\\in\\mathbb C^{QN}$ is the\n'
        'received pilot vector for the candidate path. Search $d\\in[0,N)$ and\n'
        '$|\\nu|\\leq\\nu_{\\max}$, where $\\nu_{\\max}$ is the maximum absolute\n'
        'Doppler shift in the channel model. Since')
    a,b = text.split(r'\subsection{Noise Variance Estimation}')
    b = b.replace(r'\frac1L', r'\frac{1}{N_{\rm s}}')
    b = re.sub(r'\bL\b', lambda _: r'N_{\rm s}', b)
    b = replace_once(b, 'taking logarithms. For a candidate spatial signal rank $j$, define',
        'taking logarithms, where $\\epsilon_{\\rm mach}$ is the machine precision.\n'
        'For a candidate spatial signal rank $j$, define')
    return a+r'\subsection{Noise Variance Estimation}'+b

def comparison(text):
    a,b=text.split(r'\subsection{Channel Representation and Matched Resources}')
    middle,c=b.split(r'\subsection{Modulation Operation Counts}')
    # Bare G only: the channel operator is outside this subsection.
    middle=re.sub(r'\bG\b', lambda _: r'N_{\rm pre}', middle)
    return a+r'\subsection{Channel Representation and Matched Resources}'+middle+\
        r'\subsection{Modulation Operation Counts}'+c

if '--resume' not in sys.argv:
    edit('04_generative_priors.tex',learning)
    edit('05_overall_algorithm.tex',algorithm)
edit('06_simulation_results.tex',simulation)
edit('appendix_parameter_estimation.tex',frontend)
edit('appendix_afdm_channel_model.tex',comparison)

# Distinguish the imaginary unit typographically from the column/rank index j.
for name in ('02_system_model.tex','06_simulation_results.tex',
             'appendix_parameter_estimation.tex','appendix_afdm_channel_model.tex'):
    edit(name, lambda text: text.replace('e^{j',r'e^{\mathrm j')
                               .replace('e^{-j',r'e^{-\mathrm j'))
print('Applied scoped symbol and definition updates.')
