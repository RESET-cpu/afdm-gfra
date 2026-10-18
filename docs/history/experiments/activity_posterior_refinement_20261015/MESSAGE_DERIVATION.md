# Activity factor messages and Gaussian expectation propagation

Independent mathematical audit, 2026-10-15. The reviewer shares the preceding research context with the parent agent but checked the identities against primary sources and independent deterministic examples. This note defines information that can be passed between factors; it does not implement or validate a new AMP receiver. Existing Proposed, AMP implementations, frozen experiments, and their results are unchanged.

## 1. Scope and source terminology

The current synthetic model integrates out the active Gaussian channel coefficients. With conditionally independent observation columns,

\[
Y_{:c}\mid a\sim\mathcal{CN}(0,\Sigma_a),\qquad
\Sigma_a=\sigma^2I_Q+q\sum_{k=1}^K a_k A_kA_k^H,
\tag{1}
\]

where \(q>0\), \(\sigma^2>0\), and \(a_k\in\{0,1\}\). The likelihood is

\[
f(Y\mid a)\propto
\exp\{-C\log\det\Sigma_a-\operatorname{tr}(Y^H\Sigma_a^{-1}Y)\}.
\tag{2}
\]

There is no real-Gaussian factor \(1/2\) in (2). The following discrete-message arguments apply to any positive likelihood, while the independent-column factorization requires the stated generative model. They do not assume a physical AFDM channel has independent Gaussian columns.

Primary-source terminology and locators:

| Term or claim | Primary source and location |
|---|---|
| Factor graph; sum-product factor-to-variable message | Kschischang, Frey, and Loeliger, *Factor Graphs and the Sum-Product Algorithm*, IEEE TIT 47(2), 498–519 (2001), [primary PDF](https://www.mit.edu/~6.454/www_fall_2002/lizhong/factorgraph.pdf), §II-C, p. 502, equations (5)–(6). The preceding text on p. 502 explicitly makes an edge message a function of that edge's variable. |
| Limits of cyclic sum-product; clustering | Same paper, §V, p. 510, and §VI-A, p. 513. Clustering changes the variable alphabet and computational cost. |
| Expectation propagation; remove, moment match, divide | Minka, *Expectation Propagation for Approximate Bayesian Inference*, UAI 2001, [author's corrected PDF](https://tminka.github.io/papers/ep/minka-ep-uai.pdf), §2, equations (4)–(6), and §3, equations (8)–(10), algorithm steps 3(b)–3(d). PDF pages 2–3. |
| Cavity distribution; tilted distribution; site approximation | Vehtari et al., *Expectation Propagation as a Way of Life: A Framework for Bayesian Inference on Partitioned Data*, JMLR 21(17), 1–53 (2020), [primary PDF](https://www.jmlr.org/papers/volume21/18-817/18-817.pdf), §2.1, pp. 5–6. These exact terms are sourced here rather than attributed verbatim to Minka's 2001 wording. |
| Gaussian site may be improper although the distributions needed in the update must be proper | Vehtari et al., §5.3, pp. 18–19. |
| Extrinsic Gaussian division in the related receiver | Cai et al., *Joint Activity Detection and Channel Estimation for Massive Connectivity: Where Message Passing Meets Score-Based Generative Priors*, [v2 original text](https://arxiv.org/html/2506.00581v2), §III-A, equations (6)–(11), and §III-B1, equations (24)–(27). Its activity posterior is in §III-B2, equations (28)–(30). |

The project-wide terminology file is outside this audit's authorized write scope. This table supplies the source records for integration by the parent agent.

## 2. Exact outgoing activity message from one observation factor

Let the entering messages be independent Bernoulli functions

\[
\nu_j(b)=\rho_j^b(1-\rho_j)^{1-b},\qquad 0<\rho_j<1.
\tag{3}
\]

For a single observation factor connected to all activity variables, sum-product gives

\[
m_{f\to k}(b)\propto
\sum_{a_{-k}}f(Y\mid a_k=b,a_{-k})
\prod_{j\ne k}\nu_j(a_j).
\tag{4}
\]

This is a function of the **single target variable** \(b\). The other variables have been summed out. It is not itself a joint function of the remaining activities. Normalizing the belief

\[
b_k(b)\propto\nu_k(b)m_{f\to k}(b)
\tag{5}
\]

gives the exact posterior marginal \(p_k=b_k(1)\) for this one-factor model. Taking odds yields

\[
\frac{p_k}{1-p_k}
=\frac{\rho_k}{1-\rho_k}
\frac{m_{f\to k}(1)}{m_{f\to k}(0)},
\qquad
\ell_{f\to k}=\operatorname{logit}p_k-\operatorname{logit}\rho_k.
\tag{6}
\]

Only the target user's entering prior is removed. Holding \(f\) and \(\nu_{-k}\) fixed, the outgoing message is unchanged by changing \(\rho_k\). It generally changes when another user's entering prior changes. Consequently it is not a likelihood ratio independent of every prior in the model.

If an iterative module instead receives current Bernoulli messages \(\nu_k^{\mathrm{in}}\), the subtraction must remove the logit actually used in that module's calculation. Subtracting the original physical prior after using a different entering message is not the same division. For a loopy sum-product approximation, the corresponding belief-division identity remains an algebraic identity for its approximate belief; it does not establish that belief as an exact marginal.

### 2.1 Stable evaluation without rounded probabilities

Define full log weights and grouped log sums

\[
w(a)=\log f(Y\mid a)+\sum_j\log\nu_j(a_j),\qquad
L_b=\operatorname{LSE}_{a:a_k=b}w(a),
\tag{7}
\]

where \(\operatorname{LSE}\) is log-sum-exp. Then

\[
\ell_{f\to k}=L_1-L_0-\operatorname{logit}\rho_k.
\tag{8}
\]

Equivalently, omit \(\log\nu_k\) before each grouped log-sum-exp. This avoids first converting to a posterior probability that may round to zero or one. With positive noise and nondegenerate Bernoulli priors, all finite-support likelihood weights in (2) are positive; an outgoing LLR can be large but finite.

Finite-chain frequencies of zero or one do not establish an exact posterior mass of zero or one. Equation (8) is exact when its sums are available. It cannot recover weights in unexplored states from an incomplete chain. Clipping an empirical probability is a separately specified regularization, not an exact implementation of the sum in (4).

## 3. Reusing a posterior as a prior reuses the likelihood

Let \(p_0(a)=\prod_k\nu_k(a_k)\). One update is

\[
p_1(a)\propto f(Y\mid a)p_0(a).
\tag{9}
\]

Using \(p_1\) as a new prior while processing the same observation factor again gives

\[
p_2(a)\propto f(Y\mid a)p_1(a)
\propto f(Y\mid a)^2p_0(a).
\tag{10}
\]

This is a different posterior. For a scalar activity with \(\rho=0.2\) and likelihood values \((1,3)\), the correct posterior activity probability is \(3/7\), while the repeated update yields \(9/13\).

Removing only a user's own prior odds from its posterior marginal does not generally undo all feedback introduced through other users' posterior-dependent entering messages. A valid iterative construction must identify the represented factors and remove or replace the old contribution. The fact that a numerical probability is called “extrinsic” is insufficient to establish this bookkeeping.

## 4. Disjoint columns: exact joint transfer and lost dependence

Under the conditional independence in (1), divide columns into disjoint groups \(Y_1,Y_2\), with \(C_1+C_2=C\). Then

\[
f(Y\mid a)=f_1(Y_1\mid a)f_2(Y_2\mid a),
\tag{11}
\]

up to an activity-independent normalization. Each group contributes

\[
\log f_j(Y_j\mid a)
=-C_j\log\det\Sigma_a
-\operatorname{tr}(Y_j^H\Sigma_a^{-1}Y_j)+c_j.
\tag{12}
\]

The **complete joint** posterior can be transferred exactly:

\[
p_1(a)\propto f_1(Y_1\mid a)p_0(a),\qquad
p_{12}(a)\propto f_2(Y_2\mid a)p_1(a).
\tag{13}
\]

If both joint posteriors were separately computed using the same prior,

\[
p_{12}(a)\propto\frac{p_1(a)p_2(a)}{p_0(a)}.
\tag{14}
\]

Neither (13) nor (14) authorizes replacing a joint distribution by the product of its marginals. Observation-induced dependencies remain even when the original prior factors. Marginalization and division generally do not commute.

A graph with two factors both connected to two or more of the same scalar activity variables contains cycles. Standard factor-to-variable messages on that graph remain scalar functions as in (4), but iterating them is generally a loopy approximation. An exact transfer between the two modules can instead retain a joint function over the shared activities, or an equivalent exact representation. Clustering all \(K\) binary activities gives an alphabet of size \(2^K\). A finite sample representation has its own approximation error and is not automatically exact.

The column factorization also needs to be checked for a physical model: integrating out latent parameters shared across columns, or retaining correlated channel columns, can destroy (11). The present deterministic controls use the synthetic independent-column model for which (11) is exact.

### 4.1 A transparent two-variable counterexample

Use support order \((00,01,10,11)\), uniform independent prior, and positive factors

\[
f_1=(1,9,9,1),\qquad f_2=(1,9,1,9).
\tag{15}
\]

After the first factor, the joint probability is \((0.05,0.45,0.45,0.05)\), with both marginals equal to \(0.5\). Thus both outgoing marginal LLRs are zero, but the activities are dependent. After incorporating the second factor, exact final marginals are \((0.18,0.90)\). Replacing the first posterior by the product of its marginals yields \((0.50,0.90)\). A set of zero marginal LLRs cannot encode the lost dependence.

This is a mathematical factor-table example, not a claimed realization of a particular AFDM observation. The QA additionally uses likelihoods of the form (2):

| Fixed construction | Exact joint sequential-update error | Maximum final marginal error after replacing the first joint posterior by its marginal product |
|---|---:|---:|
| \(K=2,Q=1,N=1,C=2\), \(A=[1,1]\), \(Y=[1,1.2]\), \(q=1,\sigma^2=0.2,\rho_k=0.1\) | \(2.22\times10^{-16}\) | 0.0861854 |
| \(K=3,Q=2,N=1,C=2\), fixed complex observation specified in `check_messages.py`, \(q=0.7,\sigma^2=0.4\) | \(8.33\times10^{-17}\) | 0.0103465 |

These constructions require no ground-truth activity or Monte Carlo sampling.

## 5. Gaussian expectation propagation: removal and replacement

Use real coordinates first, including real and imaginary parts when the unknown is complex. Write the target as

\[
p(x)\propto f_0(x)\prod_i f_i(x),\qquad
q(x)\propto f_0(x)\prod_i\widetilde f_i(x),
\tag{16}
\]

where the retained base factor \(f_0\) and site approximations are chosen so that \(q\) is Gaussian. If the base factor is not Gaussian, it must also be approximated or otherwise accommodated; the Gaussian equations below do not make an arbitrary base factor Gaussian.

A Gaussian site is an unnormalized positive function with natural parameters

\[
\widetilde f_i(x)\propto
\exp\{-\tfrac12x^T\Lambda_i x+h_i^Tx\}.
\tag{17}
\]

Let the current global Gaussian have precision \(\Lambda\) and precision-weighted mean \(h\). Remove the old site to form the cavity:

\[
q^{\setminus i}(x)\propto\frac{q(x)}{\widetilde f_i(x)},\qquad
\Lambda_c=\Lambda-\Lambda_i,\quad h_c=h-h_i.
\tag{18}
\]

For a proper Gaussian cavity, \(\Lambda_c\succ0\), with \(V_c=\Lambda_c^{-1}\) and \(m_c=V_ch_c\). Form the normalized tilted distribution using the exact factor:

\[
\widehat p_i(x)=\frac{f_i(x)q^{\setminus i}(x)}
{\int f_i(u)q^{\setminus i}(u)\,du}.
\tag{19}
\]

Provided its moments exist and its covariance is positive definite, project onto the Gaussian family by matching

\[
m_i=\mathbb E_{\widehat p_i}[x],\qquad
V_i=\operatorname{Cov}_{\widehat p_i}(x),\qquad
q_i^\star=\mathcal N(m_i,V_i).
\tag{20}
\]

The Gaussian moment projection also minimizes \(\operatorname{KL}(\widehat p_i\|q_i^\star)\) over nonsingular Gaussians. The new site is obtained by division:

\[
\widetilde f_i^\star(x)\propto\frac{q_i^\star(x)}{q^{\setminus i}(x)},\qquad
\Lambda_i^\star=V_i^{-1}-\Lambda_c,\quad
h_i^\star=V_i^{-1}m_i-h_c.
\tag{21}
\]

Replace the old site in the global approximation; do not multiply the whole tilted or projected posterior into the old global posterior. The scalar precision relation is

\[
\tau_i^\star=\frac1{v_i}-\frac1{v_c},\qquad
h_i^\star=\frac{m_i}{v_i}-\frac{m_c}{v_c}.
\tag{22}
\]

Here \(v_i\) is the posterior variance of the same tilted distribution used to obtain \(m_i\). An empirical query MSE, a network prediction-error estimate, or a conditional active-only variance is not automatically that quantity. A Bernoulli activity mixture additionally contributes the between-component variance to the full posterior moment.

For a proper complex Gaussian restriction, the natural form is

\[
\widetilde f_i(z)\propto
\exp\{-z^H\Lambda_i z+2\operatorname{Re}(h_i^Hz)\},
\qquad \Lambda=V^{-1},\quad h=V^{-1}m.
\tag{23}
\]

The subtraction in (18) and (21) is unchanged. A general nonlinear or mixture tilted distribution can have nonzero pseudocovariance. Restricting its projection to a proper complex Gaussian matches its mean and Hermitian covariance but not all real second moments. Matching the full real covariance requires real coordinates or an equivalent augmented representation.

### 5.1 A negative site precision is possible with exact moments

Take the proper scalar cavity and exact factor

\[
q^{\setminus i}(x)=\mathcal N(x;0,1),\qquad
f_i(x)=\tfrac12\mathcal N(x;3,1)+\tfrac12\mathcal N(x;-3,1).
\tag{24}
\]

Their normalized product is exactly

\[
\widehat p_i(x)=\tfrac12\mathcal N(x;1.5,0.5)
+\tfrac12\mathcal N(x;-1.5,0.5).
\tag{25}
\]

Its mean is zero and variance \(0.5+1.5^2=11/4\). The projected Gaussian has precision \(4/11\), so the new site has

\[
\tau_i^\star=\frac4{11}-1=-\frac7{11},\qquad
\tau_c+\tau_i^\star=\frac4{11}>0.
\tag{26}
\]

The site alone is not a normalizable Gaussian density; the tilted distribution and the global Gaussian projection are proper. Thus “a ratio of Gaussian densities is a Gaussian density” needs a positive-definite precision-difference condition. A conjugate linear-Gaussian likelihood adds a positive-semidefinite precision, so the difference is nonnegative; it can still be singular and fail to define a proper density in unobserved directions. Even nonnegativity is not automatic for nonlinear or mixed tilted distributions.

This distinction also bounds the precision-difference expressions in the related Cai receiver: their algebra describes a Gaussian factor, and interpreting it as a positive-variance observation requires the appropriate sign condition. A negative site precision cannot be inverted and supplied as a positive AWGN noise variance while retaining the same derivation. Clipping it changes the update and would need a separate approximation rationale.

Geometric damping of sites corresponds to damping their natural parameters, with consistent removal and replacement of the old site (Vehtari et al., §5.2, pp. 17–18). It is not a general guarantee of convergence or positive definiteness of every required cavity. EP division itself also does not derive or authorize adding an AMP Onsager term to this construction.

## 6. Deterministic numerical verification

The authorized new script is `experiments/activity_posterior_refinement_20261015/check_messages.py`. It contains fixed finite sums and scalar quadrature, runs on a single CPU numerical thread, and does not call the channel simulator, receiver, training code, MCMC, or truth files. The result is `results/activity_posterior_refinement_20261015/MESSAGE_QA.json`.

Run status: **6 tests passed**, no failures or errors; tolerance \(10^{-10}\); completed 2026-10-15 09:21:25 UTC. Total recorded time was 0.01146 seconds. This tolerance applies to deterministic identities, not to sampling or inference accuracy.

| Check | Recorded evidence |
|---|---|
| Exact factor LLR, stable extreme LLR, and invariance to own entering prior | Maximum identity error \(2.22\times10^{-16}\); own-prior invariance error \(7.77\times10^{-16}\); finite LLR 1000 recovered directly. Changing another user's prior changes the outgoing message. |
| Repeated observation | \(3/7\) becomes \(9/13\); repeated update equals likelihood squared to \(5.55\times10^{-17}\). |
| Dependent two-variable factor table | Exact and marginal-product final probabilities differ by 0.32. |
| Gaussian independent-column split, K2 and K3 | Likelihood factorization errors at most \(8.88\times10^{-16}\); joint sequential update errors at most \(2.22\times10^{-16}\); marginal-product errors given above. |
| Conjugate Gaussian cavity, tilted moments, site quotient | Maximum identity error \(8.88\times10^{-16}\); new site precision 1.25 and precision-weighted mean −0.875. |
| Negative precision example (24)–(26) | Analytic moments agree with independent scalar quadrature at displayed precision; quotient error \(4.44\times10^{-16}\). |

Script SHA256: `ede61d83cf4218a9294b89d0068469c3b5891e30fab7d8ea1e3f65a2ec2ce592`.

These checks establish the algebra and exhibit failure of marginal-product substitution. They do not validate a receiver that feeds estimated probabilities back into the same observation model, and they do not establish an AWGN query law or AMP state evolution.

## 7. Read-only audit of the new activity sampler

Separately reviewed `informed.py`, `test_informed.py`, and the saved `DETERMINISTIC_QA.json` in this experiment's directories. No sampler or receiver run was started by this audit.

For the implemented undirected graph, every single-bit flip and active/inactive swap has base edge weight one. Let \(\pi(x)>0\) be the fixed target mass, and define

\[
w(x,y)=\sqrt{\pi(y)/\pi(x)},\quad
Z(x)=\sum_{y\sim x}w(x,y),\quad q(y\mid x)=w(x,y)/Z(x).
\tag{27}
\]

Direct substitution into the Metropolis–Hastings ratio gives

\[
\frac{\pi(y)q(x\mid y)}{\pi(x)q(y\mid x)}
=\frac{Z(x)}{Z(y)}.
\tag{28}
\]

The degree is \(K+|x|(K-|x|)\), but no extra degree factor is required in (28): the implemented \(Z\) is the raw edge-weight sum, not a normalization relative to a uniform-neighbor Markov kernel. The fixed 0.1 holding step preserves stationarity. Flips connect the finite state graph when probabilities are positive; this theoretical fact does not bound finite-chain mixing time, and numerical underflow or extreme concentration can further restrict realized exploration.

The implementation correctly retains every post-burn state, including MH rejection and lazy holding, and aggregates all four chains with equal weight. It uses the fixed all-zero, all-one, and two independent public-prior initializations. Caches contain deterministic target/proposal values rather than retained estimates or truth. The reported conditional mean is averaged over complete sampled supports, not obtained by inserting marginal probabilities into one inverse.

The saved five-test QA reports maximum detailed-balance error \(1.39\times10^{-16}\), stationarity error \(2.22\times10^{-16}\), and support-mixture mean error \(4.34\times10^{-17}\). Its negative control without the MH accept/reject step has invariant mass proportional to \(\pi(x)Z(x)\), with total variation 0.17524 and maximum marginal bias 0.07868 in the fixed test. These observations support the kernel and bookkeeping implementation; they do not prove finite-budget posterior approximation accuracy for the larger experiment.

Reviewed sampler SHA256: `7baeadba4109349503be5e4fe2aa3dbe3caadee4e33bae5c8e7854496a111bfb`; test SHA256: `7af044bef80d9c150b3064ea5ca805a7f04379db0158daa82a3a08a4ede53d72`; unchanged target SHA256: `05d37bdfeb7c602bb48cbd6e19137e9d6fbc818e395821daec7fe4f9507850ef`.

No blocking mathematical or accounting defect was found in this bounded read-only review. The activity sampler targets the integrated Gaussian model in (1); neither it nor its small-state QA repairs the preceding AMP closed loop or establishes applicability to the physical neural channel prior.

### 7.1 Subsequent square-root failure and bounded proposal review

The parent subsequently completed the square-root sampler's registered small-scale experiment. `small/SUMMARY.json` reports that the gate **failed**: maximum marginal error 0.5, maximum individual-chain marginal error 1.0, and maximum support total variation 0.75. No K40 experiment was launched for that failed candidate. These results remain preserved. The five deterministic QA passes above concern kernel correctness, not successful finite-budget sampling.

The separately saved `SQRT_INITIALIZATION_DIAGNOSIS.json` evaluates the public all-one initialization. In case 47, its most likely proposal increases log target mass by 558.9983, yet its log MH acceptance is −45.3484. The total probability of leaving this initial state in one transition is \(2.3998\times10^{-20}\). This is compatible with detailed balance: a very large \(Z(y)/Z(x)\) can reject a favorable proposed state. The diagnosis uses public initial states and the target, without truth.

Read-only inspection of `bounded.py`, `test_bounded.py`, and `bounded/DETERMINISTIC_QA.json` confirms that the new separate candidate changes the balancing weights to

\[
g(r)=\frac{r}{1+r},\qquad g(r)=r\,g(1/r),\qquad
Z_g(x)=\sum_{y\sim x}g\!\left(\frac{\pi(y)}{\pi(x)}\right).
\tag{29}
\]

The balancing-function identity gives the same MH ratio \(Z_g(x)/Z_g(y)\) on this symmetric unit-edge graph. The implementation evaluates its log weight as `-logaddexp(0, -delta)` and keeps the MH acceptance, holding probability, initialization, and retained-state bookkeeping inherited from the frozen sampler. This is a proposal-weight change, not replacement of MH by a Barker acceptance rule. The independent source review records this balancing function in Zanella's [2017 v1 original paper](https://arxiv.org/pdf/1711.07424v1), Table 1 and §4.1, p. 8; see the local `SOURCES.md` for the original-text check and scope. The bound below is derived directly here rather than imported as a mixing theorem from that paper.

For any neighbor with \(\pi(y)\ge\pi(x)\), let \(r=\pi(y)/\pi(x)\). Including the fixed hold probability, the implemented transition satisfies

\[
P(x,y)=0.9\,g(r)\min\{Z_g(x)^{-1},Z_g(y)^{-1}\}
\ge\frac{0.45}{D_{\max}},\qquad
D_{\max}=K+\left\lfloor K^2/4\right\rfloor.
\tag{30}
\]

Indeed, \(g(r)\ge1/2\) for \(r\ge1\), while \(Z_g(x)\le d(x)\le D_{\max}\) at every state. This is a lower bound on the one-transition probability of a **specified nondecreasing neighbor edge**. It equals 0.01875 for K8 and approximately 0.00102273 for K40. It prevents the preceding exponential suppression on such an edge. It does not rule out separated modes requiring a decrease in target mass, give a spectral-gap or mixing-time bound, or ensure that the registered finite budget is adequate.

The saved four-test bounded QA reports detailed-balance error \(2.78\times10^{-17}\), stationarity error \(1.11\times10^{-16}\), and zero retained-accounting error. In its K5 example, all nondecreasing edges obey the lower bound 0.0409091; the smallest observed transition is 0.0714531. No substantive formula or accounting defect was found in this additional read-only review. It provides no claim that the new candidate passes the subsequent registered sampling experiment.
