\section{Turbo Message Passing Framework}




The posterior in  combines the observation
likelihood with the channel and activity priors.
Following the turbo message-passing framework in , we
formulate the inference as iterations between linear estimation and joint
denoising, as shown in Fig.~.
Linear estimation combines the received pilots with a Gaussian input message
to estimate .
Joint denoising uses the channel prior  and activity prior
 to estimate each .
Information is exchanged between the two estimators through Gaussian
extrinsic messages based on expectation propagation .





\subsection{Linear Estimation}


The linear estimator receives a Gaussian message from joint denoising.
This message has mean matrix 
and per-column covariance , with .
For each column, the product of this message and the likelihood in
 gives a Gaussian posterior.
The posterior mean matrix and per-column covariance are given by
:




Here,  is the average posterior variance of the  coefficients
in each column.

For message exchange, the posterior covariance is approximated by
 .
Dividing this Gaussian approximation by the incoming message removes the
information supplied by joint denoising .
The resulting extrinsic variance and mean are




Reorganizing  by device gives the tensor inputs to joint
denoising, with common variance .

\subsection{Joint Channel Estimation and Activity Detection}


The relation  couples the channel and device activity.
Following , we first derive the channel estimate
under the active hypothesis and the posterior activity probability, and then
combine them to estimate .
Let  and  denote the input mean and variance.
This Gaussian input message corresponds to the local observation model




\subsubsection{Channel Estimation}


Under the active hypothesis ,  is an AWGN
observation of the channel.
Combining its likelihood with the prior  gives the normalized
conditional posterior :



The conditional mean and covariance are



Here  in the covariance integral.
The conditional mean is the MMSE channel estimate under the active
hypothesis, and the covariance describes the corresponding estimation
uncertainty.
These moments are evaluated under the full channel prior, preserving the
dependence among the entries of  in the posterior calculation.
We denote the approximations to  and  by
 and , respectively.

\subsubsection{Activity Detection}


Activity detection compares the hypotheses  and .
Marginalizing the channel under the active hypothesis yields the likelihood
, whereas  is the Gaussian noise density under the
inactive hypothesis:



The active likelihood  also normalizes the channel posterior in
.
With prior activity probability , Bayes' rule gives



Thus, the posterior activity probability is determined by the two
likelihoods and the activity prior.
Let  denote the approximation to  used in the joint
estimate below.

\subsubsection{Joint Estimation and Extrinsic Message}


Under the two activity hypotheses,  is either zero or equal to .
The posterior mean and covariance follow by averaging the conditional
channel moments over these hypotheses:




The first covariance term represents channel uncertainty under the active
hypothesis.
The second accounts for uncertainty in whether the device is active
, .
Approximating the active-channel posterior by a Gaussian with mean 
and covariance  gives the Bernoulli--Gaussian approximation




To obtain the spatial covariance, we rearrange  into
, with one row for each antenna.
Averaging the resulting covariance over the  channel positions gives




The scalar posterior variance is then obtained by averaging its trace over
devices and antennas:




To form the extrinsic message, we use a Gaussian approximation with mean
 and common variance .
Let .
Dividing this approximation by the incoming Gaussian message, as in
, gives




For , this message has a finite, positive variance.
Its means are collected into , and 
supplies the input variance for the next linear estimation step.

The message updates above require the conditional channel moments in
 and the activity probability in
.
With the full channel prior, these integrals generally do not admit
closed-form expressions.
Section~ develops methods for learning approximations to
these quantities from channel samples, and Section~
incorporates them into the complete receiver algorithm.


\section{Learning Channel and Activity Denoisers}


The conditional channel moments in
 require integration over the
full channel prior.
These moments can be expressed in terms of score functions and estimated
by learning a channel denoiser .
We first derive these relations and the corresponding training objective
under colored Gaussian perturbations.
We then learn the density ratio between the two activity hypotheses to
obtain the activity probability in .

\subsection{Bridging Score Function and MMSE Denoising}


Consider the channel observation under the active hypothesis in
.
For a complex-valued channel sample , we stack the
real and imaginary parts of  in .
To allow for correlated errors, we consider an independent proper
complex Gaussian perturbation with covariance , giving the real
observation




At fixed , let  denote the density of
.
The conditional mean is given by Tweedie's formula





The gradient  is the
first-order score function.
In , this score gives the correction from the
noisy observation to the MMSE estimate.
For ,  gives the real representation of
the conditional mean in .

The conditional covariance  is
similarly related to the second-order score ,
:



Here the second-order score is the Hessian of the log density.
Equations~ and  thus
relate the channel moments to derivatives of the perturbed channel
density without evaluating the posterior integrals.
We next learn the first-order score from channel samples and use the
resulting mean function to calculate the required variance.

\subsection{First-Order Score Matching}


Let  approximate the first-order score.
For each fixed covariance , score matching minimizes the squared
difference between  and the score of
.
We use the covariance-weighted objective




This objective cannot be evaluated directly because the score of
 is unknown.
However, the Gaussian perturbation in  has the
known conditional score .
Using this conditional score, denoising score matching
 gives the objective



The two objectives differ by a term independent of .

To obtain the channel estimate directly, we parameterize the score as
, where  is a mean function.
Substituting this relation into 
gives the training loss




The expectation is taken over the clean channels, perturbation
covariances, and Gaussian noise.
For each fixed , the conditional mean  minimizes this loss over unrestricted mean functions.
Thus, training with  also learns the first-order
score through the above parameterization.

During message passing, the denoiser receives observations with
different noise variances.
We therefore train over a range of perturbation variances, as in
.
The input errors in the finite-dimensional multi-frame model can also be
correlated.
To account for this correlation, we corrupt clean channel samples with
colored Gaussian noise of covariance  in antenna--output--input order and condition the network on
 .
The covariance factors and the sampling law for  are specified in
Section~.

Reshaping the real and imaginary outputs of  defines the
complex mean map .
For the scalar-variance message in , we evaluate
 at .
The network architecture and preconditioning are given in
Section~.

\subsection{Variance from Conditional-Mean Derivatives}


The joint posterior moments in  require both
the conditional channel mean and variance.
Differentiating  with respect to  at fixed
 gives the output-by-input Jacobian .
Right-multiplying by  and using , we
obtain 




The trace includes the variances of the real and imaginary components;
division by  therefore gives the variance per complex coordinate.
At , this reduces to .
Thus, the required conditional variance can be computed from derivatives of
the conditional mean.

We estimate this trace using Monte Carlo finite differences
, with  in place of the conditional
mean.
Let  be independent random sign vectors with , and define .
The resulting estimate is




The conditional variance estimates used in message passing are then obtained
by setting .
Their use in the receiver is described in Section~, and the
finite-difference settings are given in Section~.

\subsection{Activity Detection via Density Ratio Estimation}


Having obtained the conditional channel mean and variance, we next consider
the activity probability.
This probability depends on the likelihoods under the active and inactive
hypotheses.
Taking the log odds of  gives



The inactive likelihood  is known, whereas  involves the
channel integral in .
Only their ratio is needed in .
We learn this density ratio through binary classification using samples from
the full channel prior .

The training data contain two classes with equal prior probability,
, where .
For , the observation is  with ; for , it
is .
The noise satisfies  independently of ,
and both classes use the same sampling law for .
The resulting class-conditional densities are therefore those in
.
The classifier logit is learned by minimizing the binary cross-entropy loss





At the population optimum over unrestricted logits, this loss recovers the
training posterior log odds:




Subtracting the training prior log odds therefore estimates the log density
ratio .
With , inserting this estimate into
 gives the receiver activity probability



where  and .
The activity prior  enters through this Bayes correction, separately
from the learned density ratio.

The classifier takes the observation together with  as input,
incorporating the channel estimate obtained from the learned prior.
The denoiser is trained first and then kept fixed during classifier
training.
Together, the denoiser, its derivative estimate, and the classifier provide
approximations to the channel moments and activity probability required in
Section~.
Both networks remain fixed during online inference.
