# Physical-channel factors and a finite-prior Gaussian EP control

## Material Passport

- Date: 2026-10-15.
- Role: bounded independent mathematical review in the academic-research-suite experiment workflow. The reviewer shares prior project context with the parent agent; the derivation below was independently checked against the stated factorization and source code.
- Status: ANALYZED. This review ran no training, receiver, sampling, or numerical experiment and makes no new empirical-success claim.
- Inputs: `docs/SYSTEM_MODEL.md` (S0–S2); `docs/JOINT_AMP.md`; `src/afdm_jadcedd/experiment/generate.py`; physical scenario and observation code; the preceding `MESSAGE_DERIVATION.md`; and the parent's proposed finite-prior control.
- Write scope: this new document only. Existing algorithms, frozen experiments, and the preceding message audit were not changed.

## 1. Decision and limits

The proposed control is mathematically useful if its target is stated as a **finite approximation to the independent-user working prior in S2**, with a fixed observation operator and exogenous positive noise variance. Every nonzero atom can remain a complete physical channel. Exact enumeration then supplies an unambiguous reference for this finite target, and Gaussian EP can be tested as a separate approximation to it.

Three distinctions are essential:

1. Independent samples from a physical channel marginal do not constitute samples from the strict conditional prior in S1 given the actual known-phase operator and signal-dependent noise variance.
2. A few full-channel atoms have low-rank covariance in the original coordinates. Use their true real linear support; do not add artificial covariance outside that support to make a matrix invertible.
3. A Gaussian information factor need not be a proper Gaussian distribution. A proper isotropic or per-beam AWGN network query imposes additional restrictions beyond the observation factor being Gaussian.

Passing this finite control would verify factor bookkeeping and characterize Gaussian EP error on its registered target. It would not establish a new continuous physical-channel posterior solver, an AMP state-evolution result, or a repaired neural receiver.

## 2. What the present physical generator conditions on

### 2.1 Source-code evidence

| Source | Relevant operation |
|---|---|
| `experiment/generate.py::_draw_nonempty_activity` | Draw complete independent Bernoulli vectors until at least one user is active, using the activity stream only. |
| `experiment/generate.py::generate_case` | Replace the activity mask without regenerating candidate geometry or path coefficients; publish the conditional marginal activity probability. Construct per-user cross-frame phase from Doppler, then form the clean superposition and set noise variance from its power. |
| `system/scenario/continuous.py::draw_scene` | Generate parameters for every candidate user using user-associated random streams. A scene-level beam geometry is shared. Activity controls transmission rather than whether a candidate has latent path parameters. |
| `system/scenario/geometry_consistent.py::draw_scene` | Replace array directions with the directions implied by the same candidate geometry used for delay and Doppler. |
| `system/scenario/continuous.py::user_channel` | Build each complete \(M\times N_{\rm out}\times N\) channel from the physical steering vectors and AFDM path matrices. |
| `system/scenario/continuous.py::full_h_and_phase` | Save zero effective channel for inactive candidates, while retaining their candidate path parameters in the scene; form cross-frame Doppler phase. |
| `system/observation.py::ReceiverInput` and `load_input` | Public saved inputs are observation, operator, positive complex noise variance, and activity prior. Directions and activity truth are not part of this saved interface. |

Let \(\xi\) contain the candidate geometry, fading, paths, and pilot variables, and let \(\alpha\) be the activity vector. The current known-phase experiment has

\[
H_k=\mathcal H_k(\xi),\quad X_k=\alpha_kH_k,\quad
A=\Phi(\xi),\quad
\sigma^2=\mathcal V(\xi,\alpha),\quad
Y=\mathcal A(X)+\sigma E,
\tag{P1}
\]

where the standardized proper complex Gaussian \(E\) is generated independently after the latent signal, operator, and noise variance have been determined. Consequently

\[
p(Y\mid X,A,\sigma^2)
=\mathcal{CN}\!\left(\operatorname{vec}Y;
\operatorname{vec}\mathcal A(X),\sigma^2I\right)
\tag{P2}
\]

is a valid conditional likelihood. This fact does not make the conditional prior equal to an unconditional training prior.

For the registered received-SNR rule, with \(C=MN_{\rm out}\),

\[
\sigma^2=\frac{\|\mathcal A(X)\|_F^2}{QC}\,10^{-s_{\rm dB}/10}.
\tag{P3}
\]

The clean power includes user cross terms. When the SNR parameter is fixed in the generative model, conditioning on the public \(\sigma^2\) conditions on a function of the complete superposition. This can couple the activities and channels of different users. It is not equivalent to observing independent channel energies. It also does not mean that a receiver necessarily reads activity truth: the distinction is between the information in a public random variable and an oracle implementation.

The operator contains the phase \(\exp(iq\beta_k)\), with \(\beta_k\) constructed from the same Doppler variables entering the physical channel. Shared latent arguments alone do not prove a particular dependence magnitude or independence. The strict prior must retain the conditioning until independence is demonstrated. Scene-level geometric variables also need not disappear when physical channel marginals are multiplied across users.

### 2.2 Nonempty activity is a joint prior

If the preconditioning Bernoulli parameter is \(p\), let \(J=\sum_k\alpha_k\) and \(Z_+=1-(1-p)^K\). The exact activity law before the additional conditioning on \(A,\sigma^2\) is

\[
\Pr(\alpha=a\mid J\ge1)
=\frac{\mathbf1\{\sum_k a_k\ge1\}}{Z_+}
\prod_kp^{a_k}(1-p)^{1-a_k}.
\tag{P4}
\]

Its one-user marginal is \(\rho=p/Z_+\), but it is not the product of Bernoulli laws with parameter \(\rho\). For distinct users,

\[
\mathbb E[\alpha_i\alpha_j\mid J\ge1]=p^2/Z_+,\qquad
\operatorname{Cov}(\alpha_i,\alpha_j\mid J\ge1)
=-p^2(1-Z_+)/Z_+^2.
\tag{P5}
\]

After additionally conditioning on the signal-dependent noise and operator, even these simple moments need not remain the same. Using the corrected marginal \(\rho\) in independent prior factors preserves only the stated marginal input, not the nonempty joint law.

If a finite control chooses to enforce the nonempty prior, exact enumeration and the approximate algorithm must both represent the same constraint. Removing the all-zero state only in enumeration creates a target mismatch. Multiplying independent Bernoulli factors with parameter \(\rho\) and then conditioning them again on nonemptiness also fails to reproduce (P4), whose preconditioning parameter is \(p\).

### 2.3 Strict S1 versus working S2

The strict conditional posterior uses the joint probability measure

\[
dp_{\rm phys}(X,H,\alpha\mid Y,A,\sigma^2)
\propto f_Y(X)\prod_k\delta_{\alpha_kH_k}(dX_k)
\,d\Pi_{\rm phys}(H,\alpha\mid A,\sigma^2).
\tag{P6}
\]

The adopted working model instead uses

\[
dq(X,H,\alpha\mid Y,A,\sigma^2)
\propto f_Y(X)\prod_k\left[
\delta_{\alpha_kH_k}(dX_k)\,
q_{{\rm tr},k}(dH_k)\,
\rho_k^{\alpha_k}(1-\rho_k)^{1-\alpha_k}\right].
\tag{P7}
\]

Equation (P7) defines a coherent inference problem for a fixed public operator and noise level. The replacement of the joint conditioned prior in (P6) is a model approximation. A further Gaussian cavity approximation is an inference approximation. These two operations should be tested and reported separately.

## 3. A minimal finite physical-channel prior

Choose \(S\) complete physical-channel atoms \(h_{ks}\in\mathbb C^D\) for each user, where \(D=NC\), and retain the zero atom. The finite prior is

\[
\mu_k(dx_k)=\sum_{s=0}^S\pi_{ks}\delta_{h_{ks}}(dx_k),\quad
h_{k0}=0,\quad
\pi_{k0}=1-\rho_k,\quad
\pi_{ks}=\rho_k\omega_{ks}\;(s\ge1),
\tag{P8}
\]

with all \(\omega_{ks}>0\) and \(\sum_{s\ge1}\omega_{ks}=1\). Equal weights \(1/S\) are a valid declared choice. One atom index identifies the user's complete channel and common activity: \(\alpha_k=\mathbf1\{s_k>0\}\). It does not select independent atoms for different beams or coefficients.

The minimal announced control uses K2/K3 and three nonzero atoms per user, all complete physical channels, a fixed PartialDFTPilot operator independent of the atom draws, and fixed positive noise. It deliberately does not reproduce conditioning on the generator's exact cross-frame phases or realized clean-power noise rule. The exact target is

\[
\Pr(s\mid Y)
\propto\exp\!\left[-\frac{1}{\sigma^2}
\left\|Y-\sum_k A_kX_k(s_k)\right\|_F^2\right]
\prod_k\pi_{k,s_k}.
\tag{P9}
\]

There are \((S+1)^K\) states: 16 or 64 for these choices. All-zero activity is allowed in this independent-prior S2 control. The normalization and all activity/channel moments can be obtained by log-sum-exp enumeration without Monte Carlo error.

Drawing the synthetic state according to the weights of this same finite bank gives a distribution-matched finite experiment. The registered 48-case control instead deliberately stratifies the generating states to cover zero, one, two, and all active users: its signals belong to the bank, but its case average is not a population Bayes-risk or population AER estimate under those weights. Applying the finite posterior to an independently generated continuous channel is also well-defined, but introduces dictionary approximation error; that channel almost surely is not an atom. Neither setting makes the finite bank the exact continuous physical prior. Three complete channel atoms preserve each atom's physical structure while severely restricting the prior's support.

With independent prior factors and one global observation factor, treating each full user block as one variable gives a star-shaped factor graph. Exact sum-product is possible in principle; its observation-to-user message sums over every other user's atom. Its exponential cost, not a need to repeat the same likelihood, motivates an approximate message representation.

## 4. Exact support coordinates and the factor of two

Define realification \(\mathcal R(x)=[\operatorname{Re}x;\operatorname{Im}x]\). Let \(U_k\) have orthonormal columns spanning

\[
\mathcal S_k=\operatorname{span}_{\mathbb R}
\{\mathcal R(h_{k1}),\ldots,\mathcal R(h_{kS})\},\qquad
r_k=\dim\mathcal S_k\le S.
\tag{P10}
\]

Use a rank-revealing SVD with a recorded numerical rank tolerance. Set

\[
z_{ks}=U_k^T\mathcal R(h_{ks}),\qquad
\mathcal R(h_{ks})=U_kz_{ks}.
\tag{P11}
\]

This is an exact representation of the retained atoms up to the declared numerical rank tolerance, not an arbitrary reduction of their antenna or AFDM coordinates. The zero atom makes the affine support a linear subspace. Reconstruction error and singular values should be saved.

For positive finite weights on all retained atoms, the prior covariance in this true support is positive definite. If a nonzero vector \(b\) had zero variance, \(b^Tz_{ks}\) would be constant on every atom. The zero atom forces that constant to zero, contradicting the fact that the nonzero atoms span the coordinates. The ambient \(2D\)-dimensional covariance is nonetheless singular whenever \(r_k<2D\).

Let \(B_k\) implement the complex user-block observation map under a fixed vectorization. For column stacking of \(X_k\in\mathbb C^{N\times C}\), \(B_k=I_C\otimes A_k\). Define

\[
G_k=\begin{bmatrix}\operatorname{Re}B_k&-\operatorname{Im}B_k\\
\operatorname{Im}B_k&\operatorname{Re}B_k\end{bmatrix}U_k,
\quad G=[G_1,\ldots,G_K],\quad y_R=\mathcal R(\operatorname{vec}Y).
\tag{P12}
\]

Implementation can apply the original tensor forward map to each basis column instead of explicitly forming the Kronecker matrix. The real observation noise has covariance \(\Gamma=(\sigma^2/2)I\), so the Gaussian observation factor has information parameters

\[
f_Y(z)\propto\exp(-\tfrac12z^T\Lambda_0z+\eta_0^Tz),\qquad
\Lambda_0=\frac{2}{\sigma^2}G^TG,\quad
\eta_0=\frac{2}{\sigma^2}G^Ty_R.
\tag{P13}
\]

The factor of two is required because \(\sigma^2=\mathbb E|W|^2\), not the variance of one real component. The quadratic exponent in (P13) differs from the direct complex residual in (P9) only by a state-independent constant.

Real support coordinates also avoid silently imposing proper complex Gaussian covariance on a finite atom set. Such a set generally has nonzero pseudocovariance. Gaussian combinations of these support coordinates need not themselves be physical channel atoms; that is part of the subsequent approximation.

## 5. Gaussian EP with an immutable observation factor

Retain (P13) exactly and approximate each user prior measure by a Gaussian site function

\[
t_k(z_k)\propto\exp(-\tfrac12z_k^T\Lambda_kz_k+\eta_k^Tz_k).
\tag{P14}
\]

The aggregate approximation is

\[
q(z)\propto f_Y(z)\prod_kt_k(z_k),\quad
\Lambda=\Lambda_0+\operatorname{blockdiag}(\Lambda_1,\ldots,\Lambda_K),\quad
\eta=\eta_0+\operatorname{concat}(\eta_1,\ldots,\eta_K).
\tag{P15}
\]

When \(\Lambda\succ0\), \(V=\Lambda^{-1}\) and \(m=V\eta\). The full aggregate can retain cross-user Gaussian covariance even though the site functions factor by user. Making \(q\) itself block independent would be an additional approximation.

Initialize sites by the exact finite-prior means and covariances in the support coordinates. With positive weights these site covariances are positive definite in exact arithmetic, and adding the positive-semidefinite observation precision yields a proper aggregate.

### 5.1 Remove one site before using its exact prior again

For user \(k\), use the aggregate marginal block \((m_k,V_{kk})\). The outgoing cavity information parameters are

\[
\Lambda_{c,k}=V_{kk}^{-1}-\Lambda_k,\qquad
\eta_{c,k}=V_{kk}^{-1}m_k-\eta_k.
\tag{P16}
\]

These are not \(\Lambda_{kk}-\Lambda_k\): the inverse of a covariance marginal includes the Schur complement of the other users. Equivalently, integrate the other variables from \(f_Y\prod_{j\ne k}t_j\). If the resulting factor is proper, it is a Gaussian cavity distribution; otherwise retain it as an information factor and do not label it a proper query distribution.

For the finite prior, its tilted weights can be evaluated directly:

\[
\log\widetilde w_{ks}=\log\pi_{ks}
-\tfrac12z_{ks}^T\Lambda_{c,k}z_{ks}+\eta_{c,k}^Tz_{ks},\qquad
w_{ks}=\exp\{\log\widetilde w_{ks}-\operatorname{LSE}_u\log\widetilde w_{ku}\}.
\tag{P17}
\]

The full posterior moments under that local tilted measure are

\[
\widehat m_k=\sum_sw_{ks}z_{ks},\qquad
\widehat V_k=\sum_sw_{ks}(z_{ks}-\widehat m_k)(z_{ks}-\widehat m_k)^T,\qquad
\widehat p_k=\sum_{s\ge1}w_{ks}.
\tag{P18}
\]

The central covariance expression is preferable to subtracting nearly equal raw second moments. It includes activity uncertainty as well as uncertainty among the active atoms. For a mixture of a zero state and an active conditional distribution, it contains

\[
\operatorname{Cov}(z_k)=p_kV_{k\mid1}
+p_k(1-p_k)m_{k\mid1}m_{k\mid1}^T.
\tag{P19}
\]

Given an invertible \(\widehat V_k\), the proposed replacement site is

\[
\Lambda_k^\star=\widehat V_k^{-1}-\Lambda_{c,k},\qquad
\eta_k^\star=\widehat V_k^{-1}\widehat m_k-\eta_{c,k}.
\tag{P20}
\]

The discrete tilted measure and a continuous Gaussian are mutually singular; their ordinary measure-theoretic KL divergence in this direction is infinite. For this finite-atom control, define (P18)–(P20) directly as **Gaussian moment matching**. Do not claim a finite KL optimum between those two measures. The algebraic natural-parameter replacement and moment identities remain well-defined.

### 5.2 Natural-parameter damping and feasibility

With a fixed starting damping coefficient \(\beta\), try

\[
\Lambda_k^{\rm new}=(1-\beta)\Lambda_k+\beta\Lambda_k^\star,\qquad
\eta_k^{\rm new}=(1-\beta)\eta_k+\beta\eta_k^\star.
\tag{P21}
\]

Rebuild (P15) from the immutable observation parameters and the proposed site array. If a required properness or finite-value check fails, halve \(\beta\) up to the registered finite budget, otherwise record the failed update. This is a declared stabilization rule, not an identity ensuring EP convergence. The announced starting value is 0.5, with 40 sweeps for the finite control; selection or changes must follow the parent's frozen protocol rather than this audit.

Do not require each \(\Lambda_k\) to be positive definite: a Gaussian site can have negative precision while the aggregate is proper. Relevant checks are:

- \(\widehat V_k\succ0\) and finite moments for forming the target site;
- \(\Lambda\succ0\) for the aggregate used to compute Gaussian marginal moments;
- the local cavity precisions required by the chosen proper-Gaussian-query interface.

Checking all users' next-query cavity precisions after a trial update is a clear, stronger interface constraint. It is not mathematically required merely to evaluate the finite sums in (P17). In fact a finite set can be reweighted by any finite quadratic exponent, even when that information factor is not a proper Gaussian density.

There are two useful algebraic checks. First, updating site \(k\) leaves its **own** cavity parameters unchanged when the other sites are fixed; other users' cavity parameters can change. Second, with a positive-definite current aggregate and a nonsingular target tilted covariance, the undamped replacement has positive-definite aggregate precision in exact arithmetic: its Schur complement for block \(k\) is exactly \(\widehat V_k^{-1}\). Convex natural-parameter interpolation therefore also preserves aggregate positive definiteness for \(0\le\beta\le1\). Loss of another user's required proper cavity remains possible and is a legitimate reason for the declared backtracking rule.

With strictly feasible starting parameters, continuity supplies a sufficiently small step in exact arithmetic. A finite backtracking budget, near-singular matrices, or finite arithmetic can still lead to a recorded failure. Neither site clipping nor diagonal jitter is part of these identities.

### 5.3 Posterior concentration and output semantics

All atom weights are positive mathematically for finite information parameters and positive prior masses. At high information strength, log weights can differ enough that some normalized weights underflow or the covariance becomes numerically rank deficient. Report the log-weight range, smallest resolved covariance eigenvalue or factorization failure, and number of numerically nonzero weights. Distinguish this numerical limit from an improper exact finite posterior. Adding variance outside the actual atom support or silently clipping precision changes the model/update.

Activity is a property of the latent atom index. A nonsingular continuous Gaussian aggregate assigns probability one to \(z_k\ne0\), so that event cannot serve as an activity estimate. Use the tilted weights in (P18). Sequential updates leave each stored probability attached to the cavity at its own update time. At termination, freeze all final sites and recompute all tilted readouts without updating them, so reported probabilities refer to one common final site state.

Report the aggregate Gaussian mean and the refreshed tilted means separately. With damping or incomplete convergence, they need not agree. Their moment-consistency residual is an iteration diagnostic, not proof of agreement with the exact finite posterior. An exact-enumeration comparison can measure that approximation error directly.

## 6. Why rank-deficient information is not an AWGN query

The observation precision \(\Lambda_0=G^T\Gamma^{-1}G\) is positive semidefinite and may be singular. The factor is still perfectly valid:

\[
f_Y(z)\propto
\exp(-\tfrac12z^T\Lambda_0z+\eta_0^Tz),\qquad
\eta_0\in\operatorname{range}(\Lambda_0).
\tag{P22}
\]

It is constant along unobserved null directions. A pseudoinverse is not a full-space noise covariance: interpreting \(\Lambda_0^+\) as such would assign zero variance in null directions, whereas the likelihood provides no information there. Keep the information form, or restrict a likelihood representation to its informed range while explicitly retaining the uninformed coordinates in the prior.

For a local message, global rank deficiency does not automatically imply a singular user cavity. If the other users have proper Gaussian incoming messages \(\mathcal N(m_j,V_j)\), exact Gaussian elimination gives

\[
S_{-k}=\Gamma+\sum_{j\ne k}G_jV_jG_j^T,\qquad
r_{-k}=y_R-\sum_{j\ne k}G_jm_j,
\tag{P23}
\]

\[
\Lambda_{c,k}=G_k^TS_{-k}^{-1}G_k,\qquad
\eta_{c,k}=G_k^TS_{-k}^{-1}r_{-k}.
\tag{P24}
\]

Since \(\Gamma\succ0\), the local precision is positive definite exactly when \(G_k\) has full column rank. The complete multiuser operator can still be rank deficient. Formula (P24) presupposes proper incoming Gaussian factors for this convolution interpretation; arbitrary negative-precision EP sites cannot be inserted as if their inverses were positive covariances. The Schur-complement information calculation remains the relevant algebra where the required Gaussian integrations exist.

Only if \(\Lambda_{c,k}\succ0\) can one write a normalized Gaussian query in these coordinates with

\[
V_{c,k}=\Lambda_{c,k}^{-1},\qquad
r_k=V_{c,k}\eta_{c,k}.
\tag{P25}
\]

Even then, equivalence to the previously trained score interface is not automatic:

- A scalar real AWGN network requires \(V_{c,k}=\tau I\) in its actual input coordinates. A proper complex network requires the matching real covariance structure and a complex variance of \(2\tau\).
- The existing joint network accepts per-beam scalar proper complex noise, constant within each beam's transform block. A generic dense real cavity covariance in finite support coordinates is a different family.
- Mapping support-coordinate Gaussian noise back by \(U_k\) gives a singular ambient covariance \(U_kV_{c,k}U_k^T\), not full-dimensional AWGN.
- Whitening changes the signal coordinates and the transformed prior. Reusing a frozen network trained on the original physical prior is not justified solely because the whitened noise is white.

Thus this finite control should use exact finite tilted sums, not an AWGN score model. A future learned interface must state which cavity family it accepts and train or approximate that family explicitly. Positive-definite site repairs cannot be presented as equivalent to (P20).

## 7. Dependencies retained and lost

The single activity variable per user couples every coefficient and beam. In (P18) the entire atom is selected together. Splitting it into independent per-beam activities loses the shared zero event and cross-beam activity uncertainty. Even if active coefficients were conditionally independent, the second term in (P19) generally generates cross-coordinate covariance.

Independent user priors in S2 discard joint conditioning effects from S1 and the exact nonempty constraint. They do not imply an independent **posterior**: the single global observation factor couples users. Exact finite enumeration retains the full joint atom distribution. Full Gaussian EP retains only a Gaussian dependence structure through means and covariances; refreshed scalar activity marginals cannot recover all support correlations or multimodality. Replacing exact posterior activity marginals as independent priors while reusing the same observation is not the site replacement in (P16)–(P21).

If two users have identical banks, weights, and pilot blocks, the exact posterior is invariant under exchanging their labels. Their marginals must be equal; they need not be exactly 0.5 unless the posterior mass is confined to the two symmetric one-active possibilities. A single truth label cannot remove this ambiguity. This control should compare distributions/moments to enumeration, not require zero activity error.

## 8. Deterministic checks needed before interpreting the finite experiment

The following are sufficient, bounded checks rather than a new receiver benchmark:

1. **Representation and likelihood:** reconstruct each complete atom from its real support coordinates; compare the original complex residual likelihood with (P13) up to a state-independent constant. Include the real/complex variance factor of two.
2. **Enumeration:** normalize every finite state and compute joint activity probabilities, channel means, and covariance. Compare with a separate direct state sum. Include nonempty-target consistency only if that constraint is actually registered.
3. **Exact Gaussian case:** replace each finite prior by a Gaussian test prior and verify one undamped site update recovers its exact information parameters. Verify the aggregate equals the direct Gaussian posterior. This is an identity test with a numerical-precision tolerance.
4. **Observation replacement:** remove the old observation site before reinserting the same one. Its information parameters must remain \((\Lambda_0,\eta_0)\); repeated replacement must not produce \(2\Lambda_0,2\eta_0\). Keeping them immutable in (P15) enforces this directly.
5. **Cavity and damping:** compare (P16) with direct Schur elimination. Updating a user's own site must leave its own cavity invariant. Verify every accepted trial obeys the declared aggregate/cavity conditions, and record failed trials and backtracking rather than altering spectra.
6. **Rank and symmetry:** include a rank-deficient likelihood in information form, without converting it into a full-space AWGN covariance. Include equal-bank/equal-pilot label symmetry; do not use truth to select one equivalent mode.
7. **Output consistency:** refresh all tilted probabilities from the frozen final site state; distinguish them from aggregate means and from stale sequential readouts. Compare EP with enumeration as an approximation, without requiring it to reproduce every finite posterior exactly.

These identity checks can pass while EP has substantial approximation error or fails its declared numerical feasibility criteria. Such outcomes are scientifically informative and should remain in the report. The later read-only implementation and saved-result review is recorded in §10.

## 9. Primary-source terms and scope

| Term or operation | Original source and locator |
|---|---|
| Factor-to-variable sum-product; message scope; clustering | Kschischang, Frey, and Loeliger, *Factor Graphs and the Sum-Product Algorithm*, IEEE TIT 47(2), 498–519 (2001), [primary PDF](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf), §II-C p. 502, equations (5)–(6); §V p. 510; §VI-A p. 513. |
| EP removal, moment matching, and site replacement | Minka, *Expectation Propagation for Approximate Bayesian Inference*, UAI 2001, [author's corrected PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf), §2 equations (4)–(6), §3 equations (8)–(10), algorithm steps 3(b)–3(d), PDF pp. 2–3. |
| Cavity, tilted distribution, Gaussian site, damping, and improper sites | Vehtari et al., *Expectation Propagation as a Way of Life: A Framework for Bayesian Inference on Partitioned Data*, JMLR 21(17), 1–53 (2020), [primary PDF](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf), §2.1 pp. 5–6, §5.2 pp. 17–18, §5.3 pp. 18–19. |

These sources were checked in the preceding message audit and are reused here with explicit locators. Equations (P4)–(P5), the finite real-support reduction, the Schur-complement properness statements, and the repeated-observation tests are direct derivations for the present control. No cited paper is claimed to prove this finite-control EP converges, to validate the physical conditional prior approximation, or to guarantee an AFDM AWGN query law. The shared terminology document remains under the parent agent's write scope.

## 10. Read-only implementation and completed-control audit

### 10.1 Implementation correspondence

Subsequently read `physical_bank.py`, `ep.py`, their deterministic tests, `run_controls.py`, and the frozen `PROTOCOL.md`. No blocking mathematical defect was found within the registered K2/K3, three-atom scope.

- The bank draws a separate physical scene for every user/atom pair, does not select on scene activity, and uses the complete `continuous.user_channel`. Its uncentered real SVD, reconstruction map, and physical tensor forward map implement (P10)–(P12). The independent pilot deliberately defines an S2 control.
- The exact reference enumerates every state using the original complex channel/observation arrays and the exponent \(-\|Y-\widehat Y(s)\|_F^2/\sigma^2\). The state weights and activity/channel moments match the same independent finite prior used by EP.
- `ObservationFactor` contains the factor of two in (P13). `aggregate` reconstructs its precision from the immutable observation term and current prior sites. `cavity` uses the inverse marginal covariance, not a block of the full precision.
- The target covariance uses the central expression in (P18); sites are replaced through (P20)–(P21). The solver does not clip negative site eigenvalues. Trial acceptance checks the aggregate and all required local cavities.
- Final diagnostics freeze the current sites and recompute all tilted weights together. The aggregate Gaussian mean/covariance are separately stored. Failure results are marked as terminal diagnostics, possibly after a partial sweep, rather than completed estimates.
- `prior_power` calculates \(\|G\mu\|^2+\sum_k\operatorname{tr}(G_kV_kG_k^T)\), divided by the number of complex observation coefficients. This includes the nonzero prior mean and cross-user mean terms, and does not use the selected generating truth. Inference is frozen before the exact reference and truth scores are computed.

The local covariance comparison uses the SVD **real support coordinates**. Replacing \(V_c\) by its diagonal depends on that coordinate basis; replacing it by \(\operatorname{tr}(V_c)I/r_k\) is invariant to orthogonal rotations within that support. Neither is a direct comparison of antenna-domain or beam-domain noise models. The ambient covariance obtained by lifting through \(U_k\) remains singular. Saved cavity anisotropy is useful for this coordinate interface, not a demonstrated need or sufficiency of a specific physical score-network noise family.

The colored Gaussian score/Hessian test is consistent with the finite convolution identities

\[
s(r)=V_c^{-1}(\widehat m(r)-r),\qquad
\nabla_rs(r)=V_c^{-1}\widehat V(r)V_c^{-1}-V_c^{-1}.
\tag{P26}
\]

These are exact for the finite prior convolved with that specified proper Gaussian covariance. They do not claim the actual iterative physical query has that distribution. The added complete single-user test is appropriate: the one user's cavity is precisely the observation factor, so its finite tilted moments equal the enumerated posterior whenever that query is proper. The parent reports six EP tests passing after this addition and six bank tests passing. This reviewer read the tests and did not rerun them. The added EP test was recorded after the formal run; its update does not alter the frozen solver used for that run.

Reviewed implementation hashes:

| File | SHA256 |
|---|---|
| `ep.py` | `fa9b45612d2c1ca39fa76143af5b6939f5808e409e754cb3776e9c452722e4a8` |
| `physical_bank.py` | `152ec46ca7071c19751be89c88675bc072dbc21daf0201a85b3b872d10648c48` |
| `run_controls.py` | `7e49fa227237520c6f477fb6229f36c120d06754da57d38cec13cbb89849575b` |
| `PROTOCOL.md` | `b56b0452b228df39996dcead9ad224fbac343388cf7697c178b10f5fa0959d71` |
| `test_ep.py` after the added single-user test | `60282c269d4dc0756ae04f399dfa1cd97a218984e4ba410c10a0b90d55f49e0b` |
| `test_physical_bank.py` | `89aad3b475239afaad933ff18380265351eb5ab26a0168a741ca3ad580a866c2` |

### 10.2 What the saved 48 cases establish

Read `results/physical_message_20261015/SUMMARY.json` and all 48 entries of `ROWS.json`, without rerunning inference. The recorded run completed in 3.8719 seconds. All cases are retained:

| Nominal SNR | CONVERGED | GAUSSIAN_DOMAIN_FAILURE | MAX_ITERATIONS |
|---|---:|---:|---:|
| −34 dB | 9 | 1 | 2 |
| −24 dB | 0 | 12 | 0 |
| −14 dB | 0 | 12 | 0 |
| −4 dB | 0 | 12 | 0 |
| Total | 9 | 37 | 2 |

Every one of the 37 recorded failures identifies the **tilted covariance** inversion. They are not recorded negative-cavity or negative-site failures. The routine additionally enforces condition number at most \(10^{12}\), which is an explicit numerical usability threshold, not the mathematical definition of a proper covariance.

In particular, 11 failure records still have a positive computed minimum eigenvalue but exceed the condition threshold; 13 report a negative minimum, and 13 report zero. Equation (P18) is positive semidefinite by construction, so a computed negative eigenvalue does not establish a negative true posterior variance. Near-singularity, rounding, and probability underflow must be distinguished. Not all failures involve zero-valued weights: K2 scene00 at −24 dB records four nonzero weights, minimum eigenvalue \(3.58\times10^{-39}\), maximum \(4.67\times10^{-16}\), and log-weight range 161.947. This is already far outside the registered condition-number policy despite retaining all four positive numerical masses.

The finite posterior remains well-defined and enumerable in these cases. A small bank can become highly concentrated after thousands of observed coefficients discriminate among a few complete alternatives, even at a low nominal per-coefficient SNR. The recorded stopping condition is the present invertible Gaussian moment interface's inability to safely invert its computed tilted covariance under the declared numerical policy. This proximate condition alone does not identify the cause in every case: the subsequent audit in §10.3 also found numerical error in some incoming cavities, and one original failure disappears after that calculation is stabilized. Neither stopping condition establishes that the physical likelihood is invalid, that the exact finite posterior has ceased to exist, or that every continuous-prior EP/score receiver must fail.

Convergence of the approximate equations is also distinct from exact posterior accuracy. Among the nine `CONVERGED` cases, the largest activity-marginal error is 0.0805081 in `K2_ambiguous_scene01/snr-34`; its prior-energy-normalized mean error is 0.216201. The two `MAX_ITERATIONS` ambiguity cases have maximum activity errors 0.199576 and 0.241952, with normalized mean errors 0.629024 and 0.618223. These are finite-model approximation diagnostics. They show that small EP moment-consistency residuals do not guarantee equality to the exact finite joint posterior, especially in an ambiguous mixture.

No new success gate is introduced here. The appropriate conclusion is that the implementation now has a verifiable finite-target factor/message interface, together with explicit numerical failures and approximation error. Moving to a learned continuous physical prior still requires a separately specified covariance/query interface and its own validation; this control does not authorize treating a rank-deficient information factor as ambient AWGN or declaring the earlier AMP framework repaired.

### 10.3 Direct Schur revision after an independent numerical audit

The independent saved-result audit by `code_runner` subsequently found that the original evaluation of (P16) can lose precision when a large own-site precision is first added to the global approximation and later subtracted from the inverse marginal covariance. The preceding small Gaussian identity tests did not cover this scale separation. Algebraic correctness of (P16) did not suffice to make its floating-point implementation accurate for every saved case.

For example, the independent audit reports the first cavity-precision entry for user 1 in `K2_scene02/snr-34` as about 0.945480 in the original saved output versus 0.0482144 from direct elimination; that run was already marked as a Gaussian-domain failure. Even `K2_scene03/snr-34`, labeled `CONVERGED` by the original implementation, has the corresponding user-0 entry 0.06229359 versus 0.06290863, about 0.00581 relative matrix discrepancy in that audit. Its activity-probability change is small, but that does not validate the original covariance or anisotropy calculation. These are reported independent-audit comparisons, not an inference rerun by this reviewer. Original cavity-based diagnostics affected by the identity discrepancy must not be described as precise evaluations of the intended Gaussian cavity.

The separately preserved `ep_schur.py` implements the same cavity by eliminating only the other blocks. Define

\[
C_{-k}=\Lambda_{0,-k,-k}+\operatorname{blockdiag}_{j\ne k}\Lambda_j,
\qquad d_{-k}=\eta_{0,-k}+\operatorname{concat}_{j\ne k}\eta_j.
\tag{P27}
\]

Then

\[
\Lambda_{c,k}=\Lambda_{0,kk}
-\Lambda_{0,k,-k}C_{-k}^{-1}\Lambda_{0,-k,k},\qquad
\eta_{c,k}=\eta_{0,k}
-\Lambda_{0,k,-k}C_{-k}^{-1}d_{-k}.
\tag{P28}
\]

The own-site natural parameters are absent from this expression. Other users' site precisions and information vectors must remain in \(C_{-k}\) and \(d_{-k}\). In the positive-definite aggregate domain, \(C_{-k}\) is a positive-definite principal submatrix, so the required elimination is defined. With a single user the formulas reduce directly to the observation information block.

Read-only comparison of `ep.py` and `ep_schur.py` confirms that the mathematical behavior change is confined to this cavity evaluation in `all_cavities`; the target, finite bank, global observation factor, site update, damping, condition-number policy, and iteration budget are unchanged. The implementation uses the immutable observation own/cross blocks and the aggregate other-only blocks with the correct information vector. The new `test_schur.py` adds a deterministic \(10^{10}\) own-site-precision case and reuses the six existing identity/control tests. This is a numerical revision of the same EP algorithm, not a third framework. Schur subtraction itself can still suffer when the cavity is nearly rank deficient, so the revision is not a blanket error or convergence guarantee.

The new run is stored separately under `results/physical_message_20261015/schur/`. Read-only examination of its summary and 48 row records gives:

| Nominal SNR | CONVERGED | GAUSSIAN_DOMAIN_FAILURE | MAX_ITERATIONS |
|---|---:|---:|---:|
| −34 dB | 10 | 0 | 2 |
| −24 dB | 0 | 12 | 0 |
| −14 dB | 0 | 12 | 0 |
| −4 dB | 0 | 12 | 0 |
| Total | 10 | 36 | 2 |

Recorded runtime is 5.0965 seconds. The only status change from the original run is `K2_scene02/snr-34`, from `GAUSSIAN_DOMAIN_FAILURE` to `CONVERGED`. The original 48 cases remain intact. This fixes a specific numerical cavity defect while leaving the finite-bank concentration and Gaussian approximation limitations visible. The scope remains a small finite prior with deliberately stratified generating states. No further prior sweep, training, or continuous physical receiver claim is supported by these results.
