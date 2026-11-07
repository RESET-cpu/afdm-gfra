# JADCE: Sections II and III

English manuscript draft, October 8, 2026.

## System Model and Problem Formulation

### Grant-Free Access and Array Channel

Consider the uplink of a low Earth orbit (LEO) satellite supporting grant-free access from $K$ single-antenna terminals. The satellite employs a uniform planar array (UPA) with $M=M_yM_z$ antennas. Each access block contains $Q$ affine frequency division multiplexing (AFDM) pilot frames, each with $N$ useful samples. The channel geometry and path coefficients remain fixed within the access block. Terminal $k$ has activity indicator $\alpha_k\in\{0,1\}$, and the receiver jointly estimates the terminal activities and their effective channels.

Let $p$ be the terminal access probability before conditioning on a nonempty access block. The activity law used to generate such blocks is

$$
p_{\rm gen}(\boldsymbol\alpha)=
 \frac{\mathbf{1}\{\sum_{k=1}^{K}\alpha_k\geq1\}}{Z}
 \prod_{k=1}^{K}p^{\alpha_k}(1-p)^{1-\alpha_k},
 \qquad Z=1-(1-p)^K.
\tag{1}
$$

Its single-terminal marginal is $\rho=p/Z$. This publicly specified marginal, together with the observations, determines the activity prior used by the receiver.

We fix the complex-envelope convention by $s_{\rm RF}(t)=\operatorname{Re}\{x(t)e^{-j2\pi f_ct}\}$ and downconversion by $e^{+j2\pi f_ct}$. A path with time-varying propagation delay $\tau(t)$ then contributes $g\,x(t-\tau(t))e^{+j2\pi f_c\tau(t)}$. Static carrier phase is absorbed into the path gain. Under the narrowband block model, envelope delays and array directions are held fixed while the first-order carrier phase variation is retained.

Denote the satellite position and velocity by $\mathbf{s}$ and $\mathbf{v}_{\rm sat}$, respectively, and the position of terminal $k$ by $\mathbf{g}_k$. With propagation speed $c_0$ and carrier frequency $f_c$, the line-of-sight direction and common terminal Doppler shift are

$$
\mathbf{u}_k=\frac{\mathbf{g}_k-\mathbf{s}}
 {\left\lVert \mathbf{g}_k-\mathbf{s}\right\rVert},
 \qquad \nu_k=-\frac{f_c}{c_0}\mathbf{v}_{\rm sat}^{\mathsf T}\mathbf{u}_k.
\tag{2}
$$

Indeed, the range $L_k=\|\mathbf g_k-\mathbf s\|$ obeys $\dot L_k=-\mathbf v_{\rm sat}^{\mathsf T}\mathbf u_k$, so the chosen envelope has Doppler $\nu_k=f_c\dot L_k/c_0$ and time factor $e^{+j2\pi\nu_kt}$. The common reference delay below is fixed at the block reference time; it does not additionally remove a common Doppler.

Let $\tau_c$ be the propagation time from the satellite to the closest ground point in the beam footprint. After compensation of this common reference delay, path $\ell$ has residual delay

$$
\tau_{k\ell}=\frac{\left\lVert \mathbf{g}_k-\mathbf{s}\right\rVert}{c_0}-\tau_c
             +\delta_\ell\tau_{{\rm spread},k},
\tag{3}
$$

where $\delta_\ell$ and $\tau_{{\rm spread},k}$ specify the relative path delay and terminal delay spread. All paths of a terminal share its spatial direction and Doppler shift, following the common spatial response model for satellite links in [1] (Sec. II-C) and the common Doppler model in [2] (Sec. II).

Let $\mu_{y,k}$ and $\mu_{z,k}$ be the projections of $\mathbf{u}_k$ onto the fixed unit axes $\mathbf e_y,\mathbf e_z$. The array reference and indexing convention are $\mathbf s_m=\mathbf s-n_y d_y\mathbf e_y-n_zd_z\mathbf e_z$. The far-field delay difference is $(n_y d_y\mu_{y,k}+n_zd_z\mu_{z,k})/c_0$; with the envelope convention above, the narrowband array response at antenna index $m=n_z+M_zn_y$ is

$$
[\mathbf{a}_k]_m=
 \exp\!\left[j2\pi\left(
 \frac{d_y}{\lambda}n_y\mu_{y,k}
 +\frac{d_z}{\lambda}n_z\mu_{z,k}\right)\right],
 \qquad \left\lVert \mathbf{a}_k\right\rVert^2=M,
\tag{4}
$$

where $\lambda=c_0/f_c$. The unknown spatial response is included in the channel to be estimated.

### AFDM Channel with Continuous Delays

Let $B=N\Delta f$ be the sampling rate, $T_s=1/B$, and $N_{\rm CPP}$ the chirp-periodic prefix (CPP) length. Following the AFDM modulation in [3] (Secs. II-B and III-A), the discrete affine Fourier transform (DAFT) matrix $\mathbf{F}_{\rm A}$ is defined by

$$
[\mathbf{F}_{\rm A}]_{rt}=\frac{1}{\sqrt N}
 \exp[-j2\pi(c_2r^2+rt/N+c_1t^2)],
 \quad r,t\in\{0,\ldots,N-1\}.
\tag{5}
$$

An AFDM pilot vector $\mathbf{p}_{qk}$ is mapped by the inverse discrete affine Fourier transform (IDAFT) to $\mathbf{s}_{qk}=\mathbf{F}_{\rm A}^{\mathsf H}\mathbf{p}_{qk}$. The prefix extends the integer-indexed samples according to

$$
s_{qk}[t]=\exp\{j2\pi c_1(t^2-\langle t\rangle_N^2)\}
              s_{qk}[\langle t\rangle_N],
 \quad -N_{\rm CPP}\leq t<0,
\tag{6}
$$

where $\langle t\rangle_N=t-N\lfloor t/N\rfloor$. The prefix covers the residual channel delay, $N_{\rm CPP}T_s\geq\max_{k,\ell}\tau_{k\ell}$. This expression retains the chirp phase over every prefix period. The frame duration is $T_{\rm frame}=(N+N_{\rm CPP})T_s$.

To define fractional delays, we specify the continuous waveform between the discrete samples. For real normalized time $\xi$, set $w_\xi=\langle\xi\rangle_N$, $\zeta_n(w)=\lfloor2c_1w+n/N\rfloor$, and

$$
\varphi_n(\xi)=\frac{1}{\sqrt N}
\exp\!\left[j2\pi\left(c_2n^2+c_1\xi^2+\frac{nw_\xi}{N}
-\zeta_n(w_\xi)w_\xi\right)\right].
\tag{6a}
$$

This is the adopted wrapped-chirp waveform model, rather than a consequence of discrete samples alone. It agrees with the IDAFT at integer useful-sample times and obeys the same cross-period chirp extension as (6). For a delay of $d=\tau/T_s$ samples, define $\eta=t-d$, $w=\langle\eta\rangle_N$, and $\zeta_{tn}=\lfloor2c_1w+n/N\rfloor$. Substitution into $\varphi_n(t-d)$ gives

$$
[\mathbf{B}_d]_{tn}=\frac{1}{\sqrt N}
 \exp\!\left[j2\pi\left(c_2n^2+c_1\eta^2
                  +\frac{nw}{N}-\zeta_{tn}w\right)\right].
\tag{7}
$$

We use the Doppler modulation convention $\exp(+j2\pi\nu tT_s)$. For useful-window start index $g$, the corresponding path matrix is

$$
\mathbf{G}(d,\nu;g)=\mathbf{F}_{\rm A}
 \operatorname{diag}\{e^{j2\pi\nu T_s(g+t)}\}_{t=0}^{N-1}\mathbf{B}_d.
\tag{8}
$$

Expanding its entries, with $2Nc_1\in\mathbb N_+$ and integer receive index $t$, gives

$$
G_{rn}=\frac{e^{j2\pi[c_1d^2+c_2(n^2-r^2)-nd/N+\nu T_sg]}}{N}
\sum_{t=0}^{N-1}
 e^{j2\pi[(n-r)/N-2c_1d+\nu T_s]t}
 e^{j2\pi\zeta_{tn}d}.
\tag{8a}
$$

The interval-wise sum is the fractional-delay form in [2] (Sec. II, eq. (5)), with Doppler signs explicitly converted: $k_{\nu,\mathrm{Huang}}=-\nu NT_s$. The useful-window phase is retained in (8) and can be included in the reference-frame path gain. At integer $d$, the final exponential in (8a) equals one.

The chirp parameters satisfy $2Nc_1\in\mathbb{N}_{+}$. At an integer delay $d$, (8) reduces to

$$
\begin{aligned}
\mathbf{G}(d,\nu;g)&=\mathbf{F}_{\rm A}\mathbf{D}_{\nu,g}
             \boldsymbol\Omega_d\boldsymbol\Pi_{d\bmod N}\mathbf{F}_{\rm A}^{\mathsf H},
 \\
 [\boldsymbol\Omega_d]_{tt}&=
 e^{j2\pi c_1[(t-d)^2-\langle t-d\rangle_N^2]},
\end{aligned}
\tag{9,10}
$$

where $\boldsymbol\Pi_l\mathbf{s}$ has entries $s[\langle t-l\rangle_N]$. Thus the full residual delay enters the prefix phase, while its remainder determines the cyclic shift.

At the reference frame, whose useful-window start is $N_{\rm CPP}$, terminal $k$ has the DAFT-domain channel

$$
\mathbf{G}_k=\sum_{\ell}g_{k\ell}
 \mathbf{G}(\tau_{k\ell}/T_s,\nu_k;N_{\rm CPP}),
 \qquad H_{kmrn}=[\mathbf{a}_k]_m[\mathbf{G}_k]_{rn}.
\tag{11}
$$

Here $g_{k\ell}$ includes the complex path gain after large-scale power compensation. The tensor $H_k\in\mathbb{C}^{M\times N\times N}$ contains all antenna, DAFT output, and DAFT input coordinates. Its spatial unfolding $\mathbf{H}_k\in\mathbb{C}^{M\times N^2}$ has rank at most one under the common spatial response assumption. The receiver learns the distribution of this full tensor from channel samples.

### Pilots and the Received Signal

We assign pilots using randomly selected rows and permuted columns of a $KN$-point discrete Fourier transform (DFT). With distinct row indices $r_q$, column permutation $c_{kn}$, and independent uniform phases $\phi_{kn}$, the pilots are

$$
P_{qkn}=\sqrt{\frac{E_p}{N}}
 e^{-j2\pi r_qc_{kn}/(KN)}e^{j\phi_{kn}},
 \qquad \sum_{n=0}^{N-1}|P_{qkn}|^2=E_p.
\tag{12}
$$

Because the terminal Doppler is common to all of its paths, moving the useful window by one frame multiplies its channel by $e^{j\beta_k}$, where $\beta_k=\operatorname{wrap}(2\pi\nu_kT_{\rm frame})$. We assume that these effective cross-frame phases are available to the receiver and absorb them into the pilot coefficients:

$$
A_{qkn}=P_{qkn}e^{jq\beta_k},\qquad q=0,\ldots,Q-1.
\tag{13}
$$

The general matrix $\mathbf{A}$ defined below is used in inference, including the terminal-dependent phases.

Define the activity-weighted channel $X_k=\alpha_kH_k$. After prefix removal and DAFT demodulation, the observation is

$$
Y_{qmr}=\sum_{k=1}^{K}\sum_{n=0}^{N-1}A_{qkn}X_{kmrn}+W_{qmr},
 \qquad W_{qmr}\sim\mathcal{CN}(0,\sigma^2).
\tag{14}
$$

Noise entries are conditionally independent. To expose the shared linear operator, set

$$
[\mathbf{Y}]_{q,mN+r}=Y_{qmr},\quad
 [\mathbf{A}]_{q,(k-1)N+n}=A_{qkn},\quad
 [\mathbf{X}]_{(k-1)N+n,mN+r}=X_{kmrn}.
\tag{15}
$$

Then

$$
\mathbf{Y}=\mathbf{A}\mathbf{X}+\mathbf{W},\quad
 \mathbf{Y}\in\mathbb{C}^{Q\times MN},\quad
 \mathbf{A}\in\mathbb{C}^{Q\times KN},\quad
 \mathbf{X}\in\mathbb{C}^{KN\times MN}.
\tag{16}
$$

This is a multiple measurement vector (MMV) model with $MN$ measurement vectors and a shared terminal activity pattern. Equivalently, $\mathbf{y}=\mathcal{A}\mathbf{x}+\mathbf{w}$, with $\mathcal{A}=\mathbf{I}_{MN}\otimes\mathbf{A}$ and $\mathbf{x}=\operatorname{vec}(\mathbf{X})$. Grouping the coordinates of each terminal uses the fixed permutation specified by (15).

The receiver is supplied with $(\mathbf{Y},\mathbf{A},\sigma^2,\rho)$. In the simulation model, the received signal-to-noise ratio (SNR) is set through the clean superposition $\mathbf{Y}_0=\mathbf{A}\mathbf{X}$:

$$
\sigma^2=\frac{\left\lVert \mathbf{Y}_0\right\rVert_F^2}{QMN}
                     10^{-\mathrm{SNR}_{\rm dB}/10}.
\tag{17}
$$

The supplied noise variance is the parameter of the complex Gaussian noise law. The inference variables are expressed in fixed training units: $\mathbf{Y}\leftarrow\mathbf{Y}/s$, $H_k\leftarrow H_k/s$, $X_k\leftarrow X_k/s$, $\mathbf{W}\leftarrow\mathbf{W}/s$, and $\sigma^2\leftarrow\sigma^2/s^2$, with a common scale $s$. We retain the same symbols for the normalized variables.

### Bayesian Formulation

Let $D=MN^2$ be the number of complex coordinates per terminal, and let $q_{\rm tr}$ denote the normalized candidate-channel distribution used for training. It is obtained by drawing terminals from the full geometry model before applying their activity masks. The receiver uses the factorized prior

$$
q(\{dH_k\},\boldsymbol\alpha)=
 \prod_{k=1}^{K}q_{\rm tr}(dH_k)
       \rho^{\alpha_k}(1-\rho)^{1-\alpha_k},
\tag{18}
$$

and forms the working posterior

$$
\begin{aligned}
 q(d\mathbf{X},\{dH_k\},\boldsymbol\alpha\mid\mathbf{Y},\mathbf{A},\sigma^2)
 &\propto e^{-\left\lVert \mathbf{Y}-\mathbf{A}\mathbf{X}\right\rVert_F^2/\sigma^2}\\
 &\quad\times\prod_{k=1}^{K}\delta_{\alpha_kH_k}(dX_k)
       q_{\rm tr}(dH_k)\rho^{\alpha_k}(1-\rho)^{1-\alpha_k}.
 \end{aligned}
\tag{19}
$$

Here $\delta_{\alpha_kH_k}$ enforces $X_k=\alpha_kH_k$. The strict physical prior conditioned on the supplied quantities is $\Pi_{\rm phys}(\{dH_k\},\boldsymbol\alpha\mid\mathbf A,\sigma^2)$: the operator shares geometric variables with the channels, and (17) makes the noise variance depend on the clean received power. It also contains the nonempty access constraint. Equation (18) replaces this conditional joint law by the candidate-channel marginal and independent activity marginals. This is a working-model approximation; the common Gaussian likelihood does not establish equality of the two posteriors.

The desired outputs are the effective channel estimate and activity probability for each terminal. Under the working posterior, their Bayesian targets are

$$
\widehat X_k=\mathbb{E}_q[X_k\mid\mathbf{Y},\mathbf{A},\sigma^2],\qquad
 p_k=q(\alpha_k=1\mid\mathbf{Y},\mathbf{A},\sigma^2),\qquad
 \widehat\alpha_k=\mathbf{1}\{p_k\geq\tfrac12\}.
\tag{20}
$$

The following receiver approximates these quantities by exchanging Gaussian messages between a linear estimator and a learned channel denoiser, with a classifier providing the activity density ratio.

## Receiver Algorithm

The receiver follows the linear-estimation and nonlinear-denoising decomposition of score-based turbo message passing [4] (Secs. III–V). The linear module incorporates $\mathbf{A}$ and $\sigma^2$. The nonlinear module processes the complete terminal channel tensor and returns its channel and activity moments. A first network provides the channel mean, a second network learns its conditional error, and an activity classifier estimates the ratio between active-channel and zero-signal query densities. Gaussian message division and moment projection connect the modules [5] (Secs. II–III).

### Linear Estimation and Extrinsic Queries

Suppose the incoming message has mean $\mathbf{X}^{\rm pri}\in\mathbb{C}^{KN\times MN}$ and common covariance $\gamma\mathbf{I}_{KN}$ for each measurement vector, with $\gamma>0$, $\sigma^2>0$, and $\mathbf A\ne\mathbf0$. Gaussian conditioning gives

$$
\begin{aligned}
\mathbf{X}_{\rm L}
 &=\mathbf{X}^{\rm pri}+\gamma\mathbf{A}^{\mathsf H}
   (\sigma^2\mathbf{I}_Q+\gamma\mathbf{A}\mathbf{A}^{\mathsf H})^{-1}
   (\mathbf{Y}-\mathbf{A}\mathbf{X}^{\rm pri}),
 \\
 \boldsymbol\Sigma_{\rm L}
 &=(\gamma^{-1}\mathbf{I}_{KN}+\sigma^{-2}\mathbf{A}^{\mathsf H}\mathbf{A})^{-1},
 \qquad t_{\rm L}=\frac{\operatorname{tr}\boldsymbol\Sigma_{\rm L}}{KN}.
\end{aligned}
\tag{21,22}
$$

The covariance eigenvalues imply $0<t_{\rm L}<\gamma$. Projecting the covariance onto $t_{\rm L}\mathbf{I}_{KN}$ and dividing out the incoming Gaussian message therefore yields positive, finite extrinsic variance:

$$
v_{\rm L}=(t_{\rm L}^{-1}-\gamma^{-1})^{-1},\qquad
 \mathbf{R}_{\rm L}=v_{\rm L}
     \left(\frac{\mathbf{X}_{\rm L}}{t_{\rm L}}
                         -\frac{\mathbf{X}^{\rm pri}}{\gamma}\right).
\tag{23}
$$

The rows of $\mathbf{R}_{\rm L}$ are reorganized into terminal tensors $R_k\in\mathbb{C}^{M\times N\times N}$ using (15). Damping of these parameters is specified in Section III-E.

Efficient evaluation uses a thin singular value decomposition (SVD) $\mathbf{A}=\mathbf{U}\operatorname{diag}(s_i)\mathbf{V}^{\mathsf H}$. Let

$$
f_{\rm L}=\frac{1}{KN}\sum_i
       \frac{\gamma s_i^2}{\sigma^2+\gamma s_i^2}.
\tag{24}
$$

Then $t_{\rm L}=\gamma(1-f_{\rm L})$, $v_{\rm L}=t_{\rm L}/f_{\rm L}$, and $\mathbf{R}_{\rm L}=\mathbf{X}^{\rm pri} +(\mathbf{X}_{\rm L}-\mathbf{X}^{\rm pri})/f_{\rm L}$. The decomposition is computed once per observation operator.

### Learning the Channel Mean and Conditional Error

The learned denoiser is trained on the pseudo additive white Gaussian noise (AWGN) model

$$
R=H+W,\qquad H\sim q_{\rm tr},\qquad
 \operatorname{vec}(W)\sim\mathcal{CN}(\mathbf{0},v\mathbf{I}_D).
\tag{25}
$$

Equation (25) is exact for the generated training queries and a surrogate for the finite-dimensional AFDM receiver queries. To see the distinction, define $\mathbf L=\gamma\mathbf A^{\mathsf H}(\sigma^2\mathbf I+\gamma\mathbf A\mathbf A^{\mathsf H})^{-1}/f_{\rm L}$. The undamped linear query obeys the identity

$$
\mathbf R_{\rm L}-\mathbf X
=(\mathbf L\mathbf A-\mathbf I)(\mathbf X-\mathbf X^{\rm pri})+\mathbf L\mathbf W.
\tag{25a}
$$

This identity does not establish that the actual error is independent, white, or Gaussian. The scalar AWGN interpretation and damping are used with this approximation explicit, as discussed for finite systems in [4] (Sec. V-B1).

Write $\mathbf{u}=(\operatorname{Re}\operatorname{vec}(R),\operatorname{Im}\operatorname{vec}(R))\in\mathbb{R}^{2D}$, define $\mathbf{h}_{\mathbb R}$ similarly, and let $\nu=v/2$. We assume the moments needed by the losses are finite; finite fourth moments and the corresponding network integrability suffice for the conditional squared-error calculations below. Positive-variance Gaussian convolution has a smooth positive density even for a channel prior supported on a lower-dimensional set. If $q_v^{\mathbb R}$ is this active query density in real coordinates, Tweedie's identities [6, 4] give

$$
\begin{aligned}
\mathbf{m}_{\mathbb R}(\mathbf{u},v)
 &=\mathbf{u}+\nu\nabla_{\mathbf{u}}\log q_v^{\mathbb R}(\mathbf{u}),
 \\
 \mathbf{C}_{\mathbb R}(\mathbf{u},v)
 &=\nu\mathbf{I}_{2D}+\nu^2\nabla_{\mathbf{u}}^2\log q_v^{\mathbb R}(\mathbf{u}).
\end{aligned}
\tag{26,27}
$$

We train $S_\theta(\mathbf{u},v)\in\mathbb{R}^{2D}$ using denoising score matching [7, 4]. For $\boldsymbol\epsilon=(\mathbf{u}-\mathbf{h}_{\mathbb R})/\sqrt\nu$, its objective is

$$
\mathcal{L}_1(\theta)=\mathbb{E}\left[
 \frac{1}{2D}\left\lVert \sqrt\nu S_\theta(\mathbf{u},v)+\boldsymbol\epsilon\right\rVert^2\right].
\tag{28}
$$

The resulting full channel mean is

$$
F_\theta(R,v)=R+\frac v2
       \left(S_{\theta,\Re}(R,v)+jS_{\theta,\Im}(R,v)\right).
\tag{29}
$$

All $M N^2$ complex coordinates are retained in this mapping.

The second network $T_\psi(\mathbf{u},v)\in\mathbb{R}^{2D}$ is trained after freezing $S_\theta$. Define the scalar readout

$$
a_\psi(R,v)=1+\nu\frac{1}{2D}\sum_{i=1}^{2D}T_{\psi,i}(\mathbf{u},v),
 \qquad \widehat\tau_\psi(R,v)=v a_\psi(R,v).
\tag{30}
$$

With $\mathbf{b}=\sqrt\nu S_\theta+\boldsymbol\epsilon$, the global-average second-order training objective is

$$
\begin{aligned}
\mathcal{L}_2(\psi)
 &=\mathbb{E}\left[\left\{
 \frac{1}{2D}\sum_{i=1}^{2D}(\nu T_{\psi,i}-b_i^2+1)
                            \right\}^2\right]\\
 &=\mathbb{E}\left[\left\{
 a_\psi(R,v)-\frac{\left\lVert F_\theta(R,v)-H\right\rVert_F^2}{Dv}
                            \right\}^2\right].
\end{aligned}
\tag{31}
$$

The second equality follows from $F_{\theta,\mathbb R}-\mathbf{h}_{\mathbb R}=\sqrt\nu\mathbf{b}$ and $2D\nu=Dv$. It identifies the statistic learned by the network: at the function-space optimum, the scalar variance readout is

$$
\tau_\theta(R,v)=\frac{1}{D}\mathbb{E}[
 \left\lVert F_\theta(R,v)-H\right\rVert_F^2\mid R,v,\alpha=1].
\tag{32}
$$

Writing $m(R,v)=\mathbb{E}[H\mid R,v,\alpha=1]$ and $\tau_{\rm C}=D^{-1}\mathbb{E}[\left\lVert H-m\right\rVert_F^2\mid R,v,\alpha=1]$, conditional orthogonality gives

$$
\tau_\theta(R,v)=\tau_{\rm C}(R,v)
             +\frac{\left\lVert F_\theta(R,v)-m(R,v)\right\rVert_F^2}{D}.
\tag{33}
$$

Thus the learned error includes the approximation error of the deployed mean. When $F_\theta=m$, it reduces to the posterior covariance trace per complex coordinate. For $U=\|F_\theta-H\|_F^2/(Dv)$, the loss decomposes as $\mathbb E[(a_\psi-\mathbb E[U\mid R,v,\alpha=1])^2]+\mathbb E[\operatorname{Var}(U\mid R,v,\alpha=1)]$. Only the complete trace is supervised: any perturbation of $T_\psi$ whose coordinates sum to zero leaves (31) unchanged. Accordingly, individual Hessian diagonal entries or per-antenna subtraces are not separately identified by this objective.

For a receiver query $(\{R_k\},v)$, we compute $F_k=F_\theta(R_k,v)$ and $\widehat\tau_k=\widehat\tau_\psi(R_k,v)$, and use the common scalar

$$
\tau_{\rm raw}=\frac1K\sum_{k=1}^{K}\widehat\tau_k,\qquad
 \tau=\max\{\tau_{\rm raw},\tau_{\min}\}.
\tag{34}
$$

This averaging fits a common isotropic Gaussian around the fixed means $F_k$, giving equal weight to each terminal's active-conditional distribution. The conditional expected negative log density, up to a constant, is $KD\log\tau+(D/\tau)\sum_k\tau_\theta(R_k,v)$. Its derivative is $KD(\tau-K^{-1}\sum_k\tau_\theta)/\tau^2$; hence the positive-risk minimizer is the average conditional error. With the constraint $\tau\geq\tau_{\min}>0$, the minimizer is its maximum with the floor, also covering zero risk. Equation (34) substitutes finite network readouts for these conditional risks.

### Activity Detection by Density Ratio Estimation

The activity classifier compares queries generated by an active channel with queries containing only noise. Their densities under (25) are

$$
\begin{aligned}
 q_{1,v}(R)&=\int\mathcal{CN}(\operatorname{vec}(R);\operatorname{vec}(H),v\mathbf{I}_D)q_{\rm tr}(dH),\\
 q_{0,v}(R)&=\mathcal{CN}(\operatorname{vec}(R);\mathbf{0},v\mathbf{I}_D).
 \end{aligned}
\tag{35}
$$

Both classes use the same training distribution of $v$. With activity label $a\in\{0,1\}$ and training class prior $\pi_{\rm tr}=1/2$, the classifier logit $z_\phi(R,v,F_\theta(R,v))$ minimizes binary cross entropy (BCE):

$$
\mathcal{L}_{\rm act}(\phi)=\mathbb{E}[
 \log(1+e^{z_\phi})-a z_\phi].
\tag{36}
$$

The local posterior underlying these targets is proportional to $\rho^a(1-\rho)^{1-a}\mathcal{CN}(R;aH,v\mathbf I_D)q_{\rm tr}(dH)$, with normalizer $(1-\rho)q_{0,v}(R)+\rho q_{1,v}(R)$. This connects channel denoising and activity inference within the same surrogate query model.

The channel mean network is frozen when its output is used as a feature. Writing $\eta_{\rm tr}=\Pr_{\rm tr}(a=1\mid R,v)$, the conditional BCE derivative is $\operatorname{sigmoid}(z)-\eta_{\rm tr}$ and its second derivative is positive. The common variance-sampling density cancels in the posterior odds. Thus, at the function-space optimum,

$$
z^*(R,v)=\operatorname{logit}\pi_{\rm tr}
                       +\log\frac{q_{1,v}(R)}{q_{0,v}(R)}.
\tag{37}
$$

This is the standard relationship between class-probability estimation and density ratio estimation [8] (Secs. III–IV). Keeping the complete $R$ in the input preserves the query information, while $F_\theta(R,v)$ provides a deterministic feature for the finite classifier. The BCE excess risk is the expected Kullback–Leibler (KL) divergence between the true and estimated training conditional Bernoulli laws. This population statement does not establish calibration of the finite classifier on actual iterative queries.

The receiver corrects for the training class prior and incorporates the terminal access marginal once:

$$
\ell_k=z_\phi(R_k,v,F_k)-\operatorname{logit}\pi_{\rm tr},\qquad
 p_k=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k),
\tag{38}
$$

where $\operatorname{logit} a=\log[a/(1-a)]$ and $\operatorname{sigmoid} b=(1+e^{-b})^{-1}$. Under unchanged class-conditional query laws, changes in $\rho$ are handled by this explicit prior-odds correction.

For implementation, the classifier receives the real and imaginary maps of $R$ and $F_\theta$, scaled by $\sqrt{2/(1+v)}$, together with

$$
\begin{aligned}
 \Big(&\log v/5,\ \log(1+e_R),\ \log(1+e_F),\\
      &\operatorname{sgn}(c_{RF})\log(1+|c_{RF}|),\
       \log(1+e_{\rm res})\Big),
 \end{aligned}
\tag{39}
$$

where $e_R=\left\lVert R\right\rVert_F^2/(Dv)$, $e_F=\left\lVert F_\theta\right\rVert_F^2/(Dv)$, $c_{RF}=\operatorname{Re}\langle R,F_\theta\rangle_F/(Dv)$, and $e_{\rm res}=\left\lVert R-F_\theta\right\rVert_F^2/(Dv)$. The feature maps have $4M$ channels. Three convolutional blocks with widths $64$, $128$, and $128$ are conditioned on $\log v/5$; a scalar readout produces $z_\phi$.

### Conditional Gaussian Messages and Joint Moments

For each terminal we retain a Gaussian site with mean $E_k$ and scalar variance $c_k$. When the query variance is within the trained range and $0<\tau<v$, Gaussian division gives the updated site

$$
c_k=(\tau^{-1}-v^{-1})^{-1},\qquad
 E_k=c_k\left(\frac{F_k}{\tau}-\frac{R_k}{v}\right).
\tag{40}
$$

The inequality makes the site precision positive; it is an acceptance condition, not a general pointwise bound on the exact posterior variance. For finite valid queries, an unsupported variance or $\tau\geq v$ retains the previous site. Invalid covariance or nonfinite network output is reported as a failed run. Combining the available site with the current query produces active-channel moments

$$
t_k=\frac{c_kv}{c_k+v},\qquad
 \mu_k=\frac{c_kR_k+vE_k}{c_k+v}.
\tag{41}
$$

An accepted update satisfies $\mu_k=F_k$ and $t_k=\tau$. Within the trained range, activity detection in (38) uses the current $R_k,v,F_k$ whether the site is updated or retained.

Outside that range, activity is computed from the normalized Gaussian site densities:

$$
\begin{aligned}
\ell_k^{\rm G}
 &=\frac{\left\lVert R_k\right\rVert_F^2}{v}
   -\frac{\left\lVert R_k-E_k\right\rVert_F^2}{c_k+v}
   -D\log\!\left(1+\frac{c_k}{v}\right),
 \\
 p_k&=\operatorname{sigmoid}(\operatorname{logit}\rho+\ell_k^{\rm G}).
\end{aligned}
\tag{42}
$$

This follows by integrating the product $\mathcal{CN}(R;H,v\mathbf I_D)\mathcal{CN}(H;E_k,c_k\mathbf I_D)$, which yields $\mathcal{CN}(R;E_k,(v+c_k)\mathbf I_D)$, and dividing by the inactive density. It is also the analytical activity rule used in the Gaussian-evidence ablation [4] (Sec. III-B2). Since the site parameters depend on the queries, this exact Gaussian integral is not an exact evidence identity for the original physical prior.

The activity probability and conditional Gaussian moments define the terminal approximation

$$
\widetilde q_k(dX_k)=(1-p_k)\delta_0(dX_k)
             +p_k\mathcal{CN}(\operatorname{vec}(X_k);\operatorname{vec}(\mu_k),t_k\mathbf{I}_D)\,dX_k.
\tag{43}
$$

Consequently, the joint mean is $\widehat X_k=p_k\mu_k$. Let $\mathbf{U}_k\in\mathbb{C}^{M\times N^2}$ be the spatial unfolding of $\mu_k$. The spatial covariance averaged over the $N^2$ channel columns is

$$
\mathbf{C}_{X,k}=p_kt_k\mathbf{I}_M
              +\frac{p_k(1-p_k)}{N^2}\mathbf{U}_k\mathbf{U}_k^{\mathsf H}.
\tag{44}
$$

These moments follow from total expectation and total covariance under (43). The first term describes active-channel uncertainty, and the second accounts for uncertainty in terminal activity. The finite classifier and channel networks define the selected approximation; they are not asserted to be the exact posterior moments of one fixed generative prior. The common variance sent to the linear module is the average trace

$$
\overline t_X=\frac{1}{KM}\sum_{k=1}^{K}\operatorname{tr}\mathbf{C}_{X,k}
 =\frac1K\sum_{k=1}^{K}\left[
 p_kt_k+p_k(1-p_k)\frac{\left\lVert \mu_k\right\rVert_F^2}{D}\right].
\tag{45}
$$

Define $b=\operatorname{clip}(\overline t_X/v,\varepsilon,1-\varepsilon)$. The outgoing Gaussian message is

$$
\gamma_{\rm out}=\frac{vb}{1-b},\qquad
 X_{k,\rm out}=\frac{\widehat X_k-bR_k}{1-b}.
\tag{46}
$$

The clipping keeps the outgoing precision positive and finite. Equation (46) divides the adjusted Gaussian with mean $\widehat X$ and variance $bv$ by the incoming Gaussian; when clipping is active, $bv$ differs from the raw mixture variance.

### Iteration Schedule and Implementation

Initialize the linear prior mean at zero and set $\gamma^{(0)}=\rho\widehat P_H$, where $\widehat P_H$ is the training average of $\left\lVert H\right\rVert_F^2/D$. Initialize $E_k=0$, $c_k=1$, and an activity history $w_k=\rho$. At iteration $i$, the linear module first computes $(R_{{\rm L},k}^{(i)},v_{\rm L}^{(i)})$. From the second iteration onward, the nonlinear query is damped as

$$
R_k^{(i)}=(1-\eta)R_k^{(i-1)}+\eta R_{{\rm L},k}^{(i)},\qquad
 v^{(i)}=(1-\eta)v^{(i-1)}+\eta v_{\rm L}^{(i)}.
\tag{47}
$$

After nonlinear estimation, the outgoing parameters are damped similarly:

$$
X_k^{{\rm pri},(i)}=(1-\eta)X_k^{{\rm pri},(i-1)}+\eta X_{k,\rm out}^{(i)},
 \qquad
 \gamma^{(i)}=(1-\eta)\gamma^{(i-1)}+\eta\gamma_{\rm out}^{(i)}.
\tag{48}
$$

Both first updates are used directly. This is arithmetic damping of the message means and variances [4] (Sec. V-B1).

The stopping rule checks $\|\widehat X^{(i)}-\widehat X^{(i-1)}\|_F/\max(\|\widehat X^{(i)}\|_F,\|\widehat X^{(i-1)}\|_F,10^{-12})$, $\max_k|p_k^{(i)}-p_k^{(i-1)}|$, and $|v^{(i)}-v^{(i-1)}|/\max(v^{(i)},v^{(i-1)})$. Each must remain below a tolerance for a fixed number of iterations. It also checks that the site update is accepted and that its precision $\lambda_k=c_k^{-1}$, natural parameter $J_k=E_k/c_k$, and activity history have stabilized. Specifically,

$$
\begin{aligned}
d_{\lambda,k}^{(i)}&=
 \frac{|\lambda_k^{(i)}-\lambda_k^{(i-1)}|}
      {\max(\lambda_k^{(i)},\lambda_k^{(i-1)})},\\
 d_{J,k}^{(i)}&=
 \frac{\left\lVert J_k^{(i)}-J_k^{(i-1)}\right\rVert}
      {\max(1,\left\lVert J_k^{(i)}\right\rVert,\left\lVert J_k^{(i-1)}\right\rVert)},\\
 \max_k\{d_{\lambda,k}^{(i)},d_{J,k}^{(i)},
         |p_k^{(i)}-w_k^{(i-1)}|\}&<\epsilon_{\rm stop},
\end{aligned}
\tag{49}
$$

with $w_k^{(i)}=0.8w_k^{(i-1)}+0.2p_k^{(i)}$. The two consecutive-iteration counters reset separately when their respective conditions fail. The activity history is used only for this check; the reported probabilities are $p_k^{(i)}$. The primary channel output is the activity-weighted $\widehat X_k=p_k\mu_k$; the conditional estimate $\mu_k$ is also retained, along with the decision in (20). Numerical stopping is not a global convergence guarantee.

**Algorithm 1: Channel and activity estimation**

**Input:** $\mathbf{Y},\mathbf{A},\sigma^2,\rho$ and trained networks $S_\theta,T_\psi,z_\phi$.

1. Normalize by the fixed scale and initialize the prior and sites. Compute the thin SVD of $\mathbf{A}$.

1. Compute the linear Gaussian mean, variance, and extrinsic query using (21)–(23); apply (47).

1. If $v$ is supported, query the mean and second networks once for each terminal, pool the variance by (34), and update the sites by (40) when $0<\tau<v$. Compute $p_k$ using the current classifier query (38). If $v$ is unsupported, retain the sites and use (42).

1. Form conditional moments, joint means, and spatial covariances using (41)–(44). Compute and damp the outgoing message using (45)–(46) and (48).

1. Update the stopping statistics and activity history. Repeat steps 2–5 until the stopping rule or iteration limit is reached.

1. Return $\widehat X_k^{\rm phys}=s\widehat X_k$, the conditional channel estimate $s\mu_k$, activity probabilities, decisions, and the stopping status. Rescale covariance outputs by $s^2$.

The current implementation uses $M=16$, $N=16$, and $D=4096$. The training bank contains 50,000 candidate channels from 12,500 scenes, with four candidates per scene; validation uses 5,000 channels from 1,250 separate scenes. Query variances are sampled uniformly in $\log v$ over $[10^{-3},100]$. Active and inactive classifier queries share each sampled variance and use independent Gaussian noise realizations. The two channel networks pack the $M$ real and imaginary antenna maps into $2M$ feature channels and use continuous log-variance conditioning. Their base channel width is 128. The first network is frozen before training the second network and classifier.

The fixed scale is $s=0.2647966453$, and the measured normalized training power is $\widehat P_H=1.0004404181$. We use $\tau_{\min}=10^{-4}$, $\varepsilon=10^{-6}$, $\eta=0.1$, and $\epsilon_{\rm stop}=10^{-4}$. At least 60 iterations are performed; both stopping checks must hold for ten consecutive iterations, with a maximum of 600 iterations. A run reaching this maximum returns its final estimate with an iteration-limit status.

With $Q\leq KN$, the one-time thin SVD costs $O(KNQ^2)$. Including the implemented spatial transformations and small-matrix decompositions, one supported iteration costs $O(QKMN^2+KM^2N^2+M^3+K(C_\theta+C_\psi+C_\phi))$, where the three $C$ terms are the per-terminal network forward costs. Each network is evaluated once per terminal and iteration; the channel mean is reused by the classifier. The Gaussian-evidence ablation omits $C_\phi$, and unsupported queries omit all network forwards. Excluding network parameters and activation storage, the main memory cost is $O(QKN+KMN^2+KM^2)$. The present weights support the fixed $M=N=16$ tensor size.

## References

1. K.-X. Li, X. Gao, and X.-G. Xia, ``Channel estimation for LEO satellite massive MIMO OFDM communications,'' *IEEE Transactions on Wireless Communications*, 2023, doi: [10.1109/TWC.2023.3252895](https://doi.org/10.1109/TWC.2023.3252895). Author version: https://arxiv.org/abs/2207.11958.

2. Y. Huang, Y. Guo, C. Guo, Y. Wang, and X. Guo, ``Prior-agnostic AFDM channel estimation for high-mobility LEO satellite communications using diffusion models,'' *IEEE Wireless Communications Letters*, vol. 15, pp. 2949–2952, 2026, doi: [10.1109/LWC.2026.3689601](https://doi.org/10.1109/LWC.2026.3689601).

3. A. Bemani, N. Ksairi, and M. Kountouris, ``Affine frequency division multiplexing for next generation wireless communications,'' arXiv:2204.12798v2, 2022. https://arxiv.org/abs/2204.12798v2.

4. C. Cai, W. Jiang, X. Yuan, and Y.-J. A. Zhang, ``Joint activity detection and channel estimation for massive connectivity: Where message passing meets score-based generative priors,'' *IEEE Journal on Selected Areas in Communications*, vol. 44, 2026, doi: [10.1109/JSAC.2026.3663274](https://doi.org/10.1109/JSAC.2026.3663274). Author version: https://arxiv.org/abs/2506.00581.

5. T. P. Minka, ``Expectation propagation for approximate Bayesian inference,'' in *Proceedings of the Seventeenth Conference on Uncertainty in Artificial Intelligence*, pp. 362–369, 2001. https://tminka.github.io/papers/ep/minka-ep-uai.pdf.

6. B. Efron, ``Tweedie's formula and selection bias,'' *Journal of the American Statistical Association*, vol. 106, no. 496, pp. 1602–1614, 2011, doi: [10.1198/jasa.2011.tm11181](https://doi.org/10.1198/jasa.2011.tm11181).

7. P. Vincent, ``A connection between score matching and denoising autoencoders,'' *Neural Computation*, vol. 23, no. 7, pp. 1661–1674, 2011, doi: [10.1162/NECO_a_00142](https://doi.org/10.1162/NECO_a_00142).

8. A. Menon and C. S. Ong, ``Linking losses for density ratio and class-probability estimation,'' in *Proceedings of the 33rd International Conference on Machine Learning*, vol. 48, pp. 304–313, 2016. https://proceedings.mlr.press/v48/menon16.html.
