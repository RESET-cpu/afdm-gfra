from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
CHECK = Path(__file__).resolve().parent
OLD = {p.name: p.read_text(encoding='utf-8') for p in (CHECK/'before/sections').glob('*.tex')}
EQUATIONS = {}
for source in OLD.values():
    for match in re.finditer(r'\\begin\{(equation|align)\}(.*?)\\end\{\1\}', source, re.S):
        for label in re.findall(r'\\label\{([^}]+)\}', match.group()):
            EQUATIONS[label] = match.group()

def eq(label):
    return EQUATIONS[label] + '\n'

def write(name, text):
    (ROOT/'sections'/name).write_text(text.strip()+'\n', encoding='utf-8', newline='\n')

figure = re.search(r'\\begin\{figure\}.*?\\end\{figure\}', OLD['03_bayesian_receiver_design.tex'], re.S).group()
figure = figure.replace('Trained $f_\\theta,z_\\phi$; activity prior $\\rho$', 'Channel prior $q_{\\rm tr}$; activity prior $\\rho$')

ch3 = r'''
\section{Bayesian Receiver Design}
\label{sec:algorithm}

The posterior in \eqref{eq:working-posterior} couples the channels
of all devices through the multi-frame observations. Computing the
estimates in \eqref{eq:targets} therefore requires marginalization
over both channel coefficients and activity states. We develop a
message-passing receiver that separates the linear observation model
from the channel and activity priors. The resulting local posterior
reveals the channel moments and activity probabilities that must be
computed from the full channel prior.

\subsection{Posterior Factorization and Message Passing}
\label{sec:receiver-structure}

The two products in \eqref{eq:working-posterior} have different
roles. The likelihood factors couple devices within each observation
column, whereas the prior factors associate each activity variable
with the entire channel tensor of that device. Following turbo
message passing \cite{ma2015,cai2026}, we group these calculations
into multi-frame linear estimation (MFLE) and generative-prior-aided
joint denoising (GPJD), respectively. MFLE uses the received pilots
to update the channel estimates; GPJD incorporates the channel and
activity priors into these estimates. This grouping retains the
dependence among the coefficients of each $H_k$ in $q_{\rm tr}$.

The two modules exchange Gaussian messages, as illustrated in
Fig.~\ref{fig:receiver-structure}. In each module, the incoming
message is combined with the corresponding likelihood or prior,
and the resulting posterior is approximated by matching its mean
and average variance. Dividing this Gaussian approximation by the
incoming message gives the extrinsic message to the other module,
as in expectation propagation \cite{minka2001,cai2026}. Both the
estimate and its uncertainty thus enter the next update. We first
derive the linear update and then determine the posterior moments
required by joint denoising.

''' + figure + r'''

\subsection{Multi-Frame Linear Estimation}
\label{sec:mfle}

Let the incoming Gaussian message have mean
$\mathbf X^{\rm pri}\in\mathbb C^{KN\times MN}$ and per-column
covariance $\gamma\I_{KN}$, where $\gamma>0$. Multiplying this
message by the Gaussian likelihood in \eqref{eq:working-posterior}
gives the linear posterior mean and covariance
\cite[Sec.~III-A]{cai2026}:
''' + eq('eq:linear-mean') + r'''
The device-dependent inter-frame phases enter through
$\widehat{\mathbf A}$; their factors $e^{j(q-q')\beta_k}$ can
prevent pilot row orthogonality from carrying over to this matrix.
We therefore retain its full Gram matrix in the posterior covariance.

To obtain a scalar-variance message, we replace
$\bm\Sigma_{\rm L}$ by $t_{\rm L}\I_{KN}$, preserving its trace.
Dividing the resulting Gaussian approximation by the incoming
message yields \cite{ma2015,minka2001}
''' + eq('eq:linear-extrinsic') + r'''
For $\widehat{\mathbf A}\ne\mathbf0$, \eqref{eq:linear-variance}
gives $0<t_{\rm L}<\gamma$, so the extrinsic variance is positive.
After reshaping $\mathbf R_{\rm L}$ by device, its Gaussian message
has the form of a likelihood for a noisy observation of
$X_k=\alpha_kH_k$. This observation supplies the local estimation
problem considered next.

\subsection{Joint Activity and Channel Denoising}
\label{sec:gpjd}

The Gaussian message from MFLE leads to the local denoising model
\cite[Sec.~III-B]{cai2026}
''' + eq('eq:pseudo-awgn') + r'''
Here $R_k$ and $v$ denote the mean and variance used by GPJD;
the scheduling of these messages is given in
Section~\ref{sec:schedule}. Under this local model, an inactive
device contributes only noise, while an active device contributes a
channel drawn from $q_{\rm tr}$. The corresponding observation
densities are
''' + eq('eq:query-densities') + r'''

Bayes' rule gives the activity probability
''' + eq('eq:local-activity') + r'''
Conditioned on activity, the same density $q_{1,v}$ normalizes the
channel posterior:
\begin{equation}
 \pi_v(dH\mid R)
 =\frac{\CN(\vect(R);\vect(H),v\I_D)}{q_{1,v}(R)}q_{\rm tr}(dH).
 \label{eq:active-channel-posterior}
\end{equation}
Its conditional mean and covariance are therefore
\begin{equation}
 \begin{aligned}
 m(R,v)&=\int H\,\pi_v(dH\mid R),\\
 \bm\Sigma_H(R,v)&=\int \vect(H-m)\vect(H-m)^{\mathsf H}
                       \pi_v(dH\mid R).
 \end{aligned}
 \label{eq:conditional-channel-integrals}
\end{equation}
Thus, both channel estimation and activity detection depend on
integrals involving the full channel prior.

Averaging over the two activity states gives the local posterior
moments of $X=\alpha H$:
''' + eq('eq:exact-local-moments') + r'''
The first covariance term describes the remaining channel
uncertainty when the device is active. The second arises from
uncertainty in the activity state itself
\cite[Secs.~III-C--III-D]{liu2018}, \cite[Sec.~III-B]{cai2026}.
Consequently, activity probabilities affect both the channel estimate
and the uncertainty returned to MFLE.

For Gaussian message passing, let $\mu_k$, $t_k$, and $p_k$
approximate the active-channel mean, its variance per complex
coordinate, and the activity probability, respectively. The local
posterior is then approximated by
''' + eq('eq:mixture') + r'''
Reshaping $\mu_k$ into $\mathbf U_k\in\mathbb C^{M\times N^2}$
with one row per antenna gives the average spatial covariance
''' + eq('eq:joint-spatial-covariance') + r'''
Averaging over devices and complex coordinates yields
''' + eq('eq:joint-average-variance') + r'''
Set $b=\clip(\overline t_X/v,\varepsilon,1-\varepsilon)$,
where $0<\varepsilon<1/2$, and use $bv$ as the variance of the
Gaussian approximation to keep the feedback variance positive.
Dividing this approximation by the incoming message gives
the feedback to MFLE:
''' + eq('eq:nonlinear-extrinsic') + r'''
The receiver is now expressed in terms of the conditional channel
moments and the activity probability. Their evaluation still
requires the integrals in \eqref{eq:query-densities} and
\eqref{eq:conditional-channel-integrals}. The next section develops
sample-based learning objectives for these quantities; their
Gaussian message representation is specified in
Section~\ref{sec:schedule}.
'''
write('03_bayesian_receiver_design.tex', ch3)

ch4 = r'''
\section{Learning Channel and Activity Denoisers}
\label{sec:learning}

The local posterior in Section~\ref{sec:gpjd} requires two kinds
of information about the channel prior: conditional channel moments
and the density ratio between the active and inactive hypotheses.
The former can be expressed through derivatives of the Gaussian-
perturbed channel density, while the latter determines the activity
probability by Bayes' rule. We derive learning objectives for both
quantities using samples from $q_{\rm tr}$.

\subsection{Conditional Mean and Denoising Score Matching}
\label{sec:channel-learning}

Consider first the conditional mean in
\eqref{eq:conditional-channel-integrals}. Following the connection
between MMSE denoising and score functions in
\cite[Sec.~IV-A]{cai2026}, we express this mean through the density
of a Gaussian-perturbed channel. Let
$\mathbf h_{\mathbb R}\in\mathbb R^{2D}$ concatenate the real
and imaginary parts of $\vect(H)$, with $H\sim q_{\rm tr}$.
For an independent proper complex Gaussian perturbation with
covariance $C\succ0$, the real observation is
''' + eq('eq:colored-query') + r'''
At fixed $C$, let $q_{\bm\Sigma}^{\mathbb R}$ denote the density
of $\mathbf u$. Tweedie's formula gives
\cite{efron2011,dytso2021}
''' + eq('eq:tweedie-mean') + r'''
For $C=v\I_D$, this is the real representation of the conditional
mean in \eqref{eq:conditional-channel-integrals}. The posterior
integral is thereby expressed as the noisy observation plus a
correction determined by the score of its density.

Although the score in \eqref{eq:tweedie-mean} is unknown, pairs of
clean and perturbed channels can be generated from $q_{\rm tr}$.
We parameterize the conditional mean by $f_\theta(\mathbf u,C)$
and minimize
''' + eq('eq:first-loss') + r'''
The expectation averages clean channels, covariances, and
perturbations. At every fixed $C$, the unrestricted population
minimizer is $\mathbf m_{\mathbb R}(\mathbf u,C)$. To relate
this objective to score learning, set
$S_\theta=\bm\Sigma^{-1}(f_\theta-\mathbf u)$.
Then \eqref{eq:first-loss} is the squared error between
$S_\theta$ and the known conditional score
$-\bm\Sigma^{-1}(\mathbf u-\mathbf h_{\mathbb R})$, weighted
by $\bm\Sigma$. It is therefore a denoising score-matching
objective \cite{vincent2011}, from which the channel mean can be
learned without evaluating the prior density.

Conditioning on $C$ makes this construction applicable to a family
of perturbation covariances \cite[Sec.~III-B]{shastri2022}.
The finite-dimensional multi-frame observation can produce
denoiser-input errors that depart from the white Gaussian
approximation. We train with colored perturbations of covariance
$C=v(R_{\rm a}\otimes\I_N\otimes R_{\rm c})$ in
antenna--output--input order, exposing the denoiser to correlated
errors at different noise levels. The covariance factors and the
sampling law for $v$ are specified in
Section~\ref{sec:training-settings}. Reshaping the real and
imaginary outputs of $f_\theta$ defines the complex mean map
$F_\theta(R,C)$. GPJD evaluates this map at $C=v\I_D$, in
accordance with its scalar-variance message model. The network
parameterization and preconditioning are given in
Section~\ref{sec:network-settings}.

\subsection{Variance from Conditional-Mean Derivatives}
\label{sec:conditional-error}

The conditional mean also determines the channel uncertainty
needed by \eqref{eq:exact-local-moments}. For
$\mathbf P_{\mathbb R}=\operatorname{Cov}(\mathbf h_{\mathbb R}
\mid\mathbf u,C)$ and the output-by-input Jacobian
$\mathbf J_m=\partial\mathbf m_{\mathbb R}/\partial\mathbf u$,
the fixed-$C$ identity in \cite[Prop.~1]{dytso2021} gives
''' + eq('eq:mean-derivative-variance') + r'''
The trace sums real and imaginary variances, so division by $D$
gives the variance per complex coordinate. At $C=v\I_D$, this
reduces to $\tau^\star=v\operatorname{div}\mathbf m_{\mathbb R}/(2D)$.
Thus, the scalar variance required by the receiver can be obtained
from derivatives of the same conditional-mean function.

We approximate this quantity by replacing the exact mean with
$f_\theta$ and estimating its derivative trace through Monte Carlo
finite differences \cite[Sec.~V-B]{metzler2014}. For independent
random sign vectors $\mathbf z_\ell$ with
$\E[\mathbf z_\ell\mathbf z_\ell^{\mathsf T}]=\I_{2D}$, set
$\mathbf w_\ell=\bm\Sigma^{1/2}\mathbf z_\ell$. The estimate is
''' + eq('eq:derivative-trace') + r'''
Both evaluations hold $C$ fixed and differentiate the complete mean
map, including the preconditioning in \eqref{eq:mean-preconditioning}.
With $\widehat\tau_k=\widehat\tau_\theta(R_k,v\I_D)$, the
common conditional variance used in the Gaussian messages is
''' + eq('eq:pooled-variance') + r'''
where $\tau_{\min}>0$ is a numerical floor. This calculation
supplies the variance estimate without training an additional
network. The finite-difference settings are given in
Section~\ref{sec:receiver-settings}.

\subsection{Activity Detection via Density Ratio Estimation}
\label{sec:density-ratio}

To obtain the activity probability, rewrite
\eqref{eq:local-activity} as
\begin{equation}
 \log\frac{p^\star(R,v)}{1-p^\star(R,v)}
 =\log\frac{\rho}{1-\rho}
  +\log\frac{q_{1,v}(R)}{q_{0,v}(R)}.
 \label{eq:activity-log-odds}
\end{equation}
The remaining quantity is the density ratio $q_{1,v}/q_{0,v}$.
We estimate it directly by binary classification \cite{menon2016},
so activity inference uses samples from the full channel prior
without replacing that prior by the Gaussian message approximation.

To construct the two classes, draw $a\in\{0,1\}$ with
$\Pr(a=1)=\pi_{\rm tr}=1/2$. For $a=1$, generate
$R=H+W$ with $H\sim q_{\rm tr}$; for $a=0$, generate $R=W$.
In both classes, $\vect(W)\sim\CN(\mathbf0,v\I_D)$
independently of $H$, and $v$ has the same sampling law.
The resulting class-conditional densities are precisely those in
\eqref{eq:query-densities}. We learn a logit by minimizing the
binary cross-entropy loss
''' + eq('eq:classifier-loss') + r'''

At the population optimum over unrestricted logits, this loss
recovers the training posterior log odds:
''' + eq('eq:ideal-logit') + r'''
Subtracting the training prior log odds therefore estimates the
log density ratio \cite[Sec.~4.2]{menon2016}. With
$F_k=F_\theta(R_k,v\I_D)$, substitution into
\eqref{eq:activity-log-odds} gives the receiver activity probability
''' + eq('eq:activity-probability') + r'''
where $\logit a=\log[a/(1-a)]$ and
$\sigmoid b=(1+e^{-b})^{-1}$. The activity prior $\rho$ enters
through this Bayes correction, separately from the learned density
ratio.

The classifier uses the observation together with $F_k$, so its
features include the channel
estimate obtained from the learned prior. We first train the
denoiser and then hold it fixed while training the classifier.
The frozen denoiser output is a deterministic function of $R$
and $v$, which preserves the population relation in \eqref{eq:ideal-logit}.
Together, the denoiser, its derivative estimate, and the classifier
provide approximations to the channel moments and activity
probability required in Section~\ref{sec:gpjd}. Both networks
remain fixed during online inference.
'''
write('04_generative_priors.tex', ch4)

algorithm = re.search(r'\\begin\{figure\}.*?\\end\{figure\}', OLD['05_overall_algorithm.tex'], re.S).group()
ch5 = r'''
\section{GP-CCD-MP-DRE Algorithm}
\label{sec:overall}

\subsection{Overall Algorithm}
\label{sec:schedule}

Substituting the learned channel moments and activity probabilities
into the message-passing framework yields GP-CCD-MP-DRE, which
combines a generative prior (GP), covariance-conditioned denoising
(CCD), message passing (MP), and density ratio estimation (DRE).
For a Gaussian input $(R_k,v)$, the denoiser gives
$F_k=F_\theta(R_k,v\I_D)$, its derivatives supply the variance
in \eqref{eq:pooled-variance}, and the classifier gives $p_k$ in
\eqref{eq:activity-probability}. These quantities determine the
joint posterior moments and hence the extrinsic message returned
to MFLE.

To represent the learned channel moments in Gaussian messages,
we use a site approximation to the channel prior
\cite[Sec.~2.1]{vehtari2020}, of the form
$\CN(\vect(H_k);\vect(E_k),c_k\I_D)$.
Dividing the Gaussian approximation with mean $F_k$ and variance
$\tau$ by the input likelihood gives
''' + eq('eq:site-update') + r'''
Combining the site with the current input then yields
''' + eq('eq:conditional-moments') + r'''
For an accepted update, these expressions recover
$\mu_k=F_k$ and $t_k=\tau$, so the site transmits the learned
conditional moments to the mixture in \eqref{eq:mixture}.
We accept the update within the training variance range when
$0<\tau<v$; otherwise, the previous site is retained.

The resulting iteration couples channel estimation and activity
detection through both the mean and covariance in
\eqref{eq:exact-local-moments}. Updated activity probabilities
change the channel estimate and its uncertainty, while the next
linear update changes the observations used by both learned
functions. The networks operate per device and remain fixed, so
their weights can be reused across $K,Q$ at fixed $M,N$.
Algorithm~1 summarizes the iteration. In normalized coordinates,
we initialize $\mathbf X^{{\rm pri},(0)}=\mathbf0$,
$\gamma^{(0)}=\rho\widehat P_H$, $E_k=0$, $c_k=1$, and
$\kappa^{(1)}=1$, where $\widehat P_H$ is the training average
of $\norm{H}_F^2/D$. The parameter estimates, normalization,
and message damping are specified below.

''' + algorithm + r'''

\subsection{Parameter Estimation and Numerical Implementation}
\label{sec:frontend}
\label{sec:variance-update}
\label{sec:damping}

The preceding posterior calculations use a fixed observation matrix
$\widehat{\mathbf A}$ and physical noise variance
$\widehat\sigma^2$. The matrix is formed from the available
inter-frame phases through \eqref{eq:effective-pilot}; when the
phases are unknown, they are estimated by variable projection
\cite{oleary2013}. For the noise variance, the spatial sample
covariance separates the signal subspace from the trailing
eigenvalues under a lower-rank spatial signal plus white noise.
The minimum description length (MDL) criterion selects the signal
rank, and the mean of the remaining eigenvalues gives
$\widehat\sigma^2$ \cite{nadakuditi2008}.
Appendix~\ref{app:frontend} gives both estimators. Their outputs
remain fixed throughout message passing.

The input variance $v$ in the local model
\eqref{eq:pseudo-awgn} describes the uncertainty after linear
estimation. Its update follows from the expected Gaussian
negative log likelihood with the current approximate posterior
\eqref{eq:mixture} held fixed \cite[Sec.~III-A]{vila2013}.
For a candidate variance $\widetilde v$, the terms depending on it
are $KD\log\widetilde v+
\sum_k\E_{\widetilde q_k}[\norm{R_k-X_k}_F^2]/\widetilde v$.
Minimizing this expression and expanding the expected squared
error gives
''' + eq('eq:query-variance-target') + r'''
The residual measures the error of the posterior mean, while
$\overline t_X$ accounts for the remaining channel and activity
uncertainty. Let $\bar v^{(i)}$ denote the damped MFLE variance
and use $v^{(i)}=\kappa^{(i)}\bar v^{(i)}$ during iteration $i$.
With new-message weight $\eta\in(0,1]$, the next scale is
''' + eq('eq:query-variance-update') + r'''
The current $v^{(i)}$ is used for both joint denoising and the
extrinsic update; the updated scale enters the following iteration.

The channel prior and online observations use the same fixed
normalization. If $s$ is the root mean square of the training-channel
coefficients, we divide $(H_k,X_k,\mathbf Y,\mathbf W)$ by $s$
and the physical noise variance by $s^2$, retaining the same symbols
for normalized quantities. The pilot matrix is unchanged.
To moderate changes between successive Gaussian messages, we apply
damping \cite[Sec.~V-B1]{cai2026} to the MFLE output for $i\geq2$:
''' + eq('eq:input-damping') + r'''
The feedback is damped with the same weight:
''' + eq('eq:output-damping') + r'''
The first input and feedback messages are used without damping.
Outside the training variance range, the retained Gaussian sites
provide the activity density ratio specified in
\eqref{eq:gaussian-evidence}. Iteration stops when the estimates
and accepted site updates have stabilized, or at the maximum
iteration count. The corresponding checks and numerical settings
are given in Section~\ref{sec:simulation-settings}.

\subsection{Computational Complexity Analysis}
\label{sec:complexity}

The observation matrix is fixed within a transmission block, so its
thin singular value decomposition (SVD),
$\widehat{\mathbf A}=\mathbf U\diag(s_i)\mathbf V^{\mathsf H}$,
can be reused across iterations. In particular,
\eqref{eq:linear-variance}--\eqref{eq:linear-extrinsic} become
''' + eq('eq:linear-fraction') + r'''
with $\mathbf R_{\rm L}=\mathbf X^{\rm pri}
+(\mathbf X_{\rm L}-\mathbf X^{\rm pri})/f_{\rm L}$.
For $Q\leq KN$, the SVD costs $O(KNQ^2)$ once per block.
Noise estimation costs $O(QNM^2+M^3)$; let $C_{\rm phase}$ denote
the phase-search, refinement, and gain-refitting cost in
Appendix~\ref{app:frontend}. Per iteration, MFLE transformations
cost $O(QKMN^2)$, spatial covariance operations cost
$O(KM^2N^2)$, and matrix factorizations cost $O(M^3)$.
If $C_\theta,C_\phi$ denote the per-device denoiser and classifier
costs, GPJD uses $1+2L_z$ denoiser evaluations and one classifier
evaluation within the training interval. Hence,
''' + eq('eq:iteration-complexity') + r'''

For $I$ iterations, the total online complexity is bounded by
''' + eq('eq:total-complexity') + r'''
where $C_{\rm phase}=0$ for supplied phases. The derivative-based
variance estimate contributes the $2L_z$ additional denoiser
evaluations per device, while all devices share the trained
parameters. Excluding these parameters and network activations,
the pilot/SVD factors, channel messages, and spatial covariance
matrices require $O(QKN+KMN^2+KM^2)$ working storage.
'''
write('05_overall_algorithm.tex', ch5)

# Retain all numerical definitions while moving them after the main argument.
ch6 = OLD['06_simulation_results.tex']
ch6 = ch6.replace(r'\subsubsection{Channel Samples and Training}',
                  '\\subsubsection{Channel Samples and Training}\n\\label{sec:training-settings}')
network = r'''
\subsubsection{Network Architectures}
\label{sec:network-settings}

The channel denoiser uses a RefineNet backbone
\cite[Appendix~A.3]{song2019} with $128$ base channels. It processes
$2M$ real/imaginary input maps over the $N\times N$ DAFT
coordinates, conditioned on $v$ and the covariance factors.
To control scales across noise levels, we extend the scalar input,
skip, and output preconditioning in \cite[Sec.~5]{karras2022}
to the covariance matrix:
''' + eq('eq:mean-preconditioning') + r'''
Here $\sigma_{\rm d}^2=1/2$ is the nominal variance per real
coordinate in normalized channel units, and $g_\theta$ is the
covariance-conditioned backbone.

The classifier takes the real and imaginary maps of $R$ and
$F_\theta(R,v\I_D)$, scaled by $\sqrt{2/(1+v)}$. Its scalar
inputs comprise the scaled log variance, logarithmic transforms
of the input, output, and residual energies normalized by $Dv$,
and a sign-preserving logarithmic transform of the real inner
product normalized by $Dv$. It produces one logit per device
and is trained from random initialization with the denoiser frozen.

'''
ch6 = ch6.replace(r'\subsubsection{Compared Receivers}', network+r'\subsubsection{Compared Receivers}')
fallback = r'''
The training variance interval is $[v_{\min},v_{\max}]
=[10^{-3},10^2]$. Outside this interval, GP-CCD-MP-DRE retains
the Gaussian sites and computes the activity probability from
their Gaussian density ratio:
''' + eq('eq:gaussian-evidence') + '\n'
anchor = 'The SNR comparison uses $1{,}000$ scenes per point;'
ch6 = ch6.replace(anchor, fallback+anchor)
stop = OLD['05_overall_algorithm.tex'].split(r'\subsubsection{Stopping Criteria}')[1].split(r'\subsection{Computational Complexity Analysis}')[0]
stop = '\\subsubsection{Stopping Criteria}\n'+stop.lstrip()
stop = stop.replace('The numerical settings are given in Section~\\ref{sec:receiver-settings}.',
                    'The tolerances and iteration limits are those in\nSection~\\ref{sec:receiver-settings}.')
ch6 = ch6.replace(r'\subsubsection{Evaluation Metrics}', stop+'\n'+r'\subsubsection{Evaluation Metrics}')
(ROOT/'sections/06_simulation_results.tex').write_text(ch6, encoding='utf-8', newline='\n')

appendix = OLD['appendix_parameter_estimation.tex']
appendix = appendix.replace(r'\section{Inter-Frame Phase Estimation}', r'\section{Phase and Noise Estimation}')
appendix = appendix.replace('\\label{app:frontend}\n',
                            '\\label{app:frontend}\n\n\\subsection{Inter-Frame Phase Estimation}\n\\label{app:phase-estimation}\n')
noise = OLD['05_overall_algorithm.tex'].split('For the physical noise variance,')[1].split(r'\subsubsection{Message Updates}')[0]
appendix += '\n\\subsection{Noise Variance Estimation}\n\\label{app:noise-estimation}\n\nFor the physical noise variance,'+noise
write('appendix_parameter_estimation.tex', appendix)
print('Revised chapters III--V; relocated training, stopping, and noise-estimation details.')
