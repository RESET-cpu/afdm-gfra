## 01_introduction

Sixth-generation (6G) wireless networks are expected to provide ubiquitous connectivity for a massive number of Internet-of-Things (IoT) devices . To serve devices in remote areas with limited terrestrial coverage, low Earth orbit (LEO) satellites complement cellular networks for applications such as smart agriculture and climate monitoring . These power-limited devices transmit short packets sporadically, with only a small fraction active at a given time . In grant-based random access, handshaking before transmission incurs significant signaling overhead, while the long propagation delay of terrestrial-satellite links further increases access latency . Accordingly, grant-free random access (GFRA) allows active devices to transmit pilots and data directly without first obtaining a grant, reducing signaling overhead and access latency in LEO satellite IoT systems .

Supporting GFRA over LEO links requires handling large delays and Doppler shifts caused by long propagation distances and high satellite mobility. The 3rd Generation Partnership Project (3GPP) Release 17 framework addresses these effects through device-side precompensation assisted by the global navigation satellite system (GNSS) . With such precompensation, many existing satellite GFRA schemes assume perfect compensation or small residual delays and Doppler shifts at the receiver . Frequent estimation and compensation increase energy consumption and reduce battery lifetime, making these schemes less suitable for power-limited remote IoT devices . This motivates reducing dependence on GNSS, consistent with the GNSS-independent operation considered in the Release 19 study on satellite access . With reduced reliance on device-side precompensation, the satellite receiver must accommodate large differential delays and Doppler shifts, which can cause severe inter-symbol and inter-carrier interference in conventional orthogonal frequency division multiplexing (OFDM) systems .

Orthogonal time frequency space (OTFS) modulation exploits the quasi-static properties of channels in the delay--Doppler domain to mitigate these effects . In , multi-frame OTFS transmission handles large differential delays and Doppler shifts at the satellite receiver, allowing devices to operate without GNSS assistance or precompensation of these offsets. However, the two-dimensional transformation in OTFS entails relatively high modulation complexity . Affine frequency division multiplexing (AFDM), based on one-dimensional chirp modulation, offers lower modulation complexity than OTFS while retaining strong Doppler robustness over doubly dispersive channels . With properly designed chirp parameters, AFDM can also achieve full diversity over such channels . This combination of low modulation complexity and full diversity makes AFDM attractive for GFRA with power-limited IoT devices.

To realize the full potential of AFDM-GFRA, accurate joint activity detection and channel estimation (JADCE) is a crucial prerequisite . Existing methods exploit sporadic device activity to formulate JADCE as a compressed sensing (CS) problem and incorporate structured priors to capture channel sparsity . The scheme in further uses a graph neural network to adaptively learn sparsity patterns, while retaining a predefined delay--Doppler grid for the sparse channel representation. In practical propagation environments, significant power leakage caused by fractional Doppler shifts and fractional time delays can weaken the sparsity of the effective channel matrix . This motivates learning effective-channel priors from data to capture channel structures beyond the assumed sparse representation .

Score-based generative models learn channel priors from samples by estimating the score function of the channel distribution . In , score-based learning is performed directly on the AFDM effective channel to address fractional delay--Doppler off-grid leakage in channel estimation. For massive random access, proposes a two-stage algorithm that first identifies active devices through a Transformer-based detector and then uses generative diffusion models for joint channel estimation and data detection. Both approaches rely on iterative posterior sampling, which requires repeated score function evaluations and incurs substantial computational cost .

The score-based turbo message passing (STMP) algorithm in incorporates generative channel priors for JADCE without iterative posterior sampling. Through Tweedie's formulas, separate first- and second-order score networks provide posterior means and variances for single-step minimum mean-squared error (MMSE) denoising under equivalent additive white Gaussian noise (AWGN) observations. However, this AWGN model is justified in the large-system limit with right-rotationally invariant random sensing matrices . In the finite-dimensional, structured multi-frame AFDM system considered here, departures from these conditions may cause a mismatch between denoiser-input errors and the white Gaussian noise used for training. A similar limitation has been highlighted for structured compression matrices in . This mismatch can degrade channel denoising accuracy and, consequently, JADCE performance. Moreover, computes activity probabilities using Gaussian extrinsic messages obtained after projecting the channel posterior onto a Gaussian distribution. In general, matching posterior means and variances does not preserve the marginal likelihood associated with a non-Gaussian channel prior. Consequently, the resulting likelihood ratio can yield inaccurate activity probabilities even when the channel posterior moments are accurately estimated. These errors further affect the activity-weighted channel estimates exchanged with the linear estimation module.

Against this background, we investigate GNSS-independent AFDM-GFRA for LEO satellite IoT systems. Our main contributions are summarized as follows:

 We develop a multi-frame AFDM transmission scheme that handles large differential delays and Doppler shifts at the satellite receiver. The derived input--output relationship retains fractional delay--Doppler effects and the chirp-periodic prefix phase for delays exceeding the useful symbol duration. Separating the phase evolution across frames yields a multiple measurement vector (MMV) model in which the effective channel of each device remains approximately constant over consecutive frames. Additional pilot frames therefore provide more observations without increasing the number of channel coefficients to be estimated.

 We learn a score-based generative prior directly from multiantenna AFDM effective-channel samples with fractional delays and Doppler shifts, without imposing sparse or grid-aligned channel assumptions. The denoiser is trained using colored Gaussian noise with different covariance matrices, and the learned prior provides channel posterior mean and variance estimates for message passing.

 We develop a message-passing JADCE receiver for the structured multi-frame AFDM observation model. The receiver comprises multi-frame linear estimation (MFLE), which suppresses inter-user interference, and generative-prior-aided joint denoising (GPJD), which performs MMSE denoising. In GPJD, a learned density-ratio estimator compares the active and inactive observation distributions under the effective-channel prior to obtain posterior probabilities of activity. These probabilities are combined with channel posterior mean and variance estimates from the learned prior to account for activity uncertainty in channel estimation. The two modules iteratively exchange Gaussian extrinsic messages. Simulation results demonstrate that the proposed receiver improves activity detection and channel estimation performance compared with STMP across different signal-to-noise ratios and pilot-frame counts. 

The remainder of this paper is organized as follows. Section presents the system model and the multi-frame AFDM input--output relationship. Sections -- describe the receiver design, the channel and activity denoisers, and the overall algorithm with its computational complexity analysis, respectively. Section presents the simulation results.

## 02_system_model

A LEO satellite with antennas serves single-antenna devices sharing pilot resources . The devices operate without GNSS or delay/Doppler precompensation .

Satellite mobility and multipath propagation produce doubly dispersive terrestrial-satellite links (TSLs) . Taking each ground device as stationary, we assume a common Doppler shift for its paths . Let be its uniform planar array (UPA) response and the time from the block start. After receiver compensation for the common delay , the impulse response is

 where , is the path count, the path gain, and the Dirac delta. The differential delay is , where is the propagation delay of path from device . The common delay is the propagation time between the satellite and the closest point within the beam footprint .

For antenna indices and , the entries of are given by Here is the wavelength; and are the element spacings and directional cosines along the two array axes . Path gains, delays, Doppler shifts, and arrival angles are approximately constant within a transmission block.

We allocate AFDM frames to pilot transmission, with chirp subcarriers per frame . Let be the pilot symbol transmitted by the -th device during the -th AFDM frame on the -th chirp subcarrier. The corresponding pilot vector is , , . Let denote the pilot matrix known at the satellite receiver, with entries . For simplicity, is chosen to satisfy , with equal pilot energy for all devices and frames . The pilot construction is given in Section .

With subcarrier spacing and sampling interval , the inverse discrete affine Fourier transform (IDAFT) gives, for ,

 where and are AFDM modulation parameters. The signal in can be represented in matrix form as where denotes the discrete affine Fourier transform (DAFT) matrix.

Assume that the chirp-periodic prefix (CPP) length is greater than or equal to the maximum differential delay, i.e., . By the chirp periodicity, the prefix samples satisfy where and . Including the CPP, each AFDM frame has duration .

To specify the waveform between sample times, for normalized time measured from the start of the useful interval in units of , define and . We use the AFDM basis waveform For integer useful samples, ; for , it satisfies the CPP relation .

After CPP removal and DAFT demodulation, the effective channel of device in frame is represented by , with . Retaining fractional delay and Doppler effects , the entries of are where maps transmitted symbol to received symbol at antenna . For a unit-gain path of normalized delay and Doppler , let denote the starting sample of the useful interval within the transmission block. The continuous time at its -th sample is , and the path matrix is

 Frame starts at . Appendix derives the entries of this matrix and its integer-delay form. Fractional delays and Doppler shifts cause power leakage in this matrix and weaken the sparsity of .

For frame , the samples after CPP removal start at . Since is common to all paths of device , yields where maps an angle to . Thus the frames observe the same up to phase rotation.

We use an indicator function to model the device activity as Let represent the probability of a device being active, i.e., , where . Each device maintains its activity state throughout a transmission block. We define and incorporate the inter-frame phase rotation into the pilot symbols as Using and , the received signal during the th AFDM frame after CPP removal and DAFT demodulation is where is an AWGN matrix with the elements i.i.d. drawn from . We express the received signal over the AFDM frames in a more compact form as where , , and . The corresponding entries are defined by We estimate the full without imposing channel sparsity . For , is underdetermined, but device inactivity gives block sparsity through . For Bayesian JADCE, let denote the effective pilot matrix formed from the available or estimated inter-frame phases, and let denote the estimated noise variance. Both quantities remain fixed during message passing, as described in Section . Let denote the channel prior used for training, which retains dependence among the entries of . Channels and activity indicators are independent across devices, and is independent of . With Bernoulli activity priors, the joint posterior distribution factorizes as 

 where and are columns of and , , enforces , and . The desired MMSE estimate and activity probability are

## 03_bayesian_receiver_design

GP-CCD-MP-DRE combines a generative prior (GP), learned by covariance-conditioned denoising (CCD) with colored perturbations, with message passing (MP) and density ratio estimation (DRE).

Following turbo message passing , the receiver alternates multi-frame linear estimation (MFLE) and generative-prior-aided joint denoising (GPJD), as shown in Fig. . The pilot matrix and noise variance remain fixed within the block.

MFLE supplies linear posterior moments; GPJD combines channel moments from the denoiser and its derivatives with activity probabilities from the classifier. Extrinsic messages divide each Gaussian posterior approximation by its incoming message, as in expectation propagation .

The incoming message has mean and per-column covariance , where . The device-dependent factors can prevent pilot row orthogonality from carrying over to , so we retain its full Gram matrix. Linear MMSE estimation with the Gaussian likelihood in gives 

 To exchange a scalar variance between the modules, we approximate by , preserving its trace. Dividing this Gaussian approximation by the incoming message yields the extrinsic variance and mean : For , the eigenvalues in give , ensuring a positive extrinsic variance.

The MFLE updates in -- can be evaluated using a thin singular value decomposition (SVD) : The extrinsic mean equivalently becomes . The SVD is reused throughout the transmission block.

GPJD uses the local denoising model 

 Here represents the uncertainty of the input to the denoiser. Under , the input densities conditioned on activity and inactivity are, respectively, Bayes' rule then gives the exact activity probability for this local model: Let and denote the channel moments conditioned on activity. The laws of conditional expectation and covariance give the moments of as The two covariance terms describe channel and activity uncertainty , . We approximate the active-channel mean by and its variance by the fixed-covariance derivative estimate in Section . Pooling across devices gives

 A Gaussian site approximation to the channel prior has form . Within the training variance range and for , dividing the Gaussian approximation with moments by the input likelihood updates the site as

 Otherwise, the previous site is retained. Combining the site with the current input gives the approximate conditional channel variance and mean: Within the training variance range, we estimate the activity probability from the output of the separately trained classifier: where is the training class prior, , and . The subtraction estimates the log density ratio (Section ). The approximate local posterior is

 Reshape into , with one row per antenna. Its average spatial covariance is

 Averaging over devices and complex coordinates gives the feedback variance

 To form the extrinsic message to MFLE, set , where . Dividing the Gaussian approximation with mean and variance per complex coordinate by the incoming Gaussian message gives Holding fixed, the Gaussian variance update applied to gives the denoiser input-variance target

 The first term is the squared residual of the joint posterior mean, and the second includes both channel and activity uncertainty. Section specifies how the module messages and this variance target are used in the iterative receiver.

## 04_generative_priors

We train a channel denoiser with colored Gaussian perturbations , derive its conditional variance from mean derivatives, and learn the activity density ratio with a binary classifier.

For an active channel , let concatenate the real and imaginary parts of . Adding an independent proper complex Gaussian perturbation with covariance gives the real observation At fixed , denote the density of by . Tweedie's formula expresses the conditional mean through the score of this perturbed density : We parameterize the mean by and train it using the squared error weighted by : The expectation averages clean channels, covariances, and perturbations. At each fixed , its unrestricted population minimizer is . Setting converts the loss to the squared score error against , weighted by : a form of denoising score matching . Conditioning on supplies the noise statistics .

To control the input and output scales across noise levels, we extend the scalar input, skip, and output preconditioning in to the covariance matrix: Here is the nominal variance per real coordinate in the normalized channel units, and is the covariance-conditioned network. Reshaping the real and imaginary outputs of gives the complex channel-mean map , evaluated at in GPJD.

For and output-by-input Jacobian , the fixed- identity in gives

 The trace sums real and imaginary variances; dividing by gives the variance per complex coordinate. For , . We replace the exact mean by and approximate the trace by Monte Carlo finite differences . Draw independent sign vectors satisfying and set . Then

 Both evaluations hold fixed and include the complete mean map in . Pooling by supplies the variance without a second network; numerical settings appear in Section .

Binary classification estimates . Sample activity with : use , , for and for . In both classes, independently of , and has the same sampling law, yielding .

The classifier receives , , and the channel estimate , and is trained with the binary cross-entropy loss The frozen denoiser makes its output a deterministic function of and . At the population optimum over unrestricted logits, binary cross-entropy recovers the training posterior log odds:

 Subtracting from the trained logit estimates the log density ratio ; adding yields .

Clean channels are sampled before activity masking, from disjoint training and validation scenes. Draw uniformly over and use covariance in antenna--output--input order; factors follow . A RefineNet backbone with base channels processes real/imaginary input maps over the DAFT coordinates, conditioned on and the covariance factors.

The denoiser is then frozen while the classifier is trained from random initialization using . The classifier takes the real and imaginary maps of and , scaled by . Its scalar inputs comprise the scaled log variance, logarithmic transforms of the input, output, and residual energies normalized by , and a sign-preserving logarithmic transform of the real inner product normalized by . It produces one logit per device. Both networks remain fixed online and operate per device, allowing the same weights at fixed across different . Dataset and optimization settings appear in Section .

## 05_overall_algorithm

Algorithm 1 combines the module updates and learned networks.

 Form from the available inter-frame phases via . When these phases are unavailable, estimate them by variable projection , as detailed in Appendix .

For the physical noise variance, use the following observation-based estimate. Let and form the spatial sample covariance Write its eigenvalues in descending order as ; values below are floored at that level before taking logarithms. For a candidate spatial signal rank , define The Wax--Kailath minimum description length (MDL) criterion, as reviewed in , gives Under a lower-rank spatial signal plus white noise, the selected rank leaves the trailing eigenvalues for noise estimation. and remain fixed during MP.

The receiver uses the same fixed normalization as the training channels. Let be the root mean square of the training-channel coefficients. Divide by and the physical noise variance by , leaving the pilot matrix unchanged. The distribution and all message updates use these normalized coordinates, with the same symbols retained. Initialize and , where is the training average of in normalized units. Set the initial sites to , , and the variance ratio to .

MFLE returns . With reshaped per device, apply new-message weight for :

 GPJD uses , held fixed during the current update. Outside , retain the sites and use their Gaussian density ratio:

 After computing the joint moments, we evaluate from and update the variance scale for the next iteration: Form the extrinsic message in using the current and damp feedback with the same for :

 The first input and feedback messages are used without damping. Algorithm 1 summarizes the complete procedure.

Stopping requires stable estimates and stable accepted site updates. For the estimate check, we monitor the relative changes in and between successive iterations, the maximum activity-probability change , and the variance-update residual The site check requires accepted updates with stable precision and natural parameter , together with a small activity-history residual . After this comparison, update , starting from . This history is used only for stopping. After at least iterations, the estimate and site checks must each hold for consecutive iterations, and the hard activity vector must remain unchanged for consecutive iterates. Otherwise, the receiver returns the last iterate at .

The numerical settings are given in Section .

For , a thin SVD of costs once per block. Noise estimation costs ; let cover the phase search, refinement, and gain refits in Appendix . Per iteration, MFLE transformations cost , spatial covariance operations , and matrix factorizations . If are per-device denoiser/classifier costs, GPJD requires denoiser passes and one classifier pass within the training interval. Hence

 For iterations, the total online complexity is bounded by For supplied phases, . Excluding trained parameters and network activations, the pilot/SVD factors, channel messages, and spatial covariance matrices require working storage.

## 06_simulation_results

We evaluate channel denoising, JADCE accuracy, pilot requirements, access load, and transfer across channel profiles.

Table specifies the satellite uplink. Devices are uniform over the beam footprint; delays, Doppler shifts, and array responses share the same geometry. Large-scale propagation effects are compensated. The NTN-TDL-D profile uses uniform delay spread ns, a line-of-sight gain of fixed amplitude and uniform phase, and proper complex Gaussian diffuse gains. Path parameters remain fixed per block. Defaults are , , and .

For , the pilots are constructed from distinct rows and permuted columns of a -point discrete Fourier transform (DFT) matrix. Let be the selected row indices, let be a permutation of , and let be independent uniform phases on . The pilot symbols satisfy where is the pilot energy of each device in each frame.

Device activities are generated independently with nominal probability , conditioned on at least one active device. The resulting marginal probability is . The receiver uses this marginal in its independent Bernoulli prior approximation. For the clean received signal , the signal-to-noise ratio (SNR) specifies the noise variance as 

Training and validation use and clean channels from disjoint scenes, with four candidate channels sampled per scene before activity masking. All use the same fixed normalization scale . The denoiser uses Adam, batch size , initial learning rate , and exponential moving average decay over epochs; the minimum fixed-noise validation loss selects the checkpoint. The white-noise reference shares the channel bank and epoch budget.

Colored training uses the proper complex Gaussian covariance in antenna--output--input order, with sampled uniformly on a logarithmic scale over and independent factors

 where has independent entries and is uniform on ; each factor has trace and varying eigenvectors/eigenvalues. After training by , freeze the denoiser and train the classifier from random initialization using binary cross-entropy and equally likely active/inactive labels. Its batch size, initial learning rate, and epoch budget are , , and ; validation selects the checkpoint. Classifier inputs use noise covariance and frozen denoiser features; receiver evaluations use the same covariance form. The selected checkpoints are epoch for the denoiser and epoch for the classifier.

 We compare GP-CCD-MP-DRE with STMP and four sparse-recovery baselines: simultaneous orthogonal matching pursuit (SOMP) , generalized approximate message passing based sparse Bayesian learning (GAMP-SBL) , GNN-ASPL , and off-grid SBL . SOMP, GAMP-SBL, and GNN-ASPL use an integer delay--Doppler dictionary; off-grid SBL additionally estimates continuous offsets through a first-order atom approximation. Their AFDM and multiantenna adaptations, trained weights, and activity readout rules are fixed throughout the reported comparisons. SOMP selects at most atoms, GAMP-SBL allows iterations, GNN-ASPL uses layers, and off-grid SBL uses iterations.

All comparisons use known inter-frame phases and observation-based noise estimates. STMP and GP-CCD-MP-DRE use activity threshold and the stopping checks in Section . The reported comparisons use and , with relative-change tolerance . The activity-change, site-parameter, and activity-history tolerances are , , and , respectively, with , , and . Their default new-message weights are and .

For GP-CCD-MP-DRE, the derivative estimate in uses and , with one random sign vector per device reused throughout a transmission block. The pooled variance floor in is .

The SNR comparison uses scenes per point; the pilot-frame, device-count, activity-probability, and cross-profile comparisons use paired scenes per point. Scenes are reused across conditions; parameter selection and evaluation details appear in Appendix .

For channel estimation, we report the normalized mean-squared error (NMSE) by pooling error and channel energies over the evaluated scenes: where . Errors on inactive devices are included. For direct channel denoising, is replaced by and the sums run over the individual channel samples. The activity error rate (AER) is where and count missed detections and false alarms, respectively. AER is reported for the SNR and pilot-frame comparisons.

Following , we evaluate denoising separately using , , with known and nominal SNR . Six SNRs span to dB; each uses scenes and four channels per scene ( samples). Both neural estimators share channel and white-noise realizations; AWGN and colored label their training perturbations.

References are least squares (LS), returning ; the Gaussian-prior estimate , where is the normalized training-channel power; and genie-aided conditional MMSE. Given true path geometry, powers, and line-of-sight gain, the genie reports the analytic conditional MSE of the remaining Gaussian gains. The four sparse-recovery kernels use an identity observation operator and known AWGN variance, retaining their receiver settings and GNN weights; GAMP-SBL retains its internal noise update.

At dB in Fig. , the colored-trained estimator reaches dB NMSE versus dB for the Gaussian-prior estimator, demonstrating the value of structure beyond average power. The learned estimators continue improving at high SNR, whereas sparse recovery flattens, consistent with residual dictionary and first-order offset approximation error. The estimator trained with colored noise gains dB over the white-trained estimator at dB, but the latter is better at high SNR. The benefit is therefore concentrated at high input uncertainty. The genie remains better, with additional path information unavailable to the learned estimators.

Figure compares the iteration trajectories at dB for one scene with five active devices.

Both trajectories initially increase in NMSE: approximate extrinsic updates do not guarantee monotonic error reduction. GP-CCD-MP-DRE approaches its final dB by about iterations, while STMP improves more slowly to dB. This is a single-scene result.

Figure compares channel NMSE and AER over to dB.

The learned receivers continue improving as SNR increases, while sparse recovery improves less, consistent with the representation constraints seen in direct denoising. The NMSE gain over STMP narrows from dB at dB to dB at dB. At dB, GP-CCD-MP-DRE reduces STMP's AER by about -4 0 K=40 p=0.1 1.57 Q=16 0.51 Q=48 -14 24 32 25 gap remains.

Figure compares GP-CCD-MP-DRE, STMP, and the four baselines for -- at dB, with and .

Increasing at fixed raises both the candidate dimension and expected active population, while each observation column still has measurements. Fixed aggregate SNR also lowers typical per-device SNR. NMSE consequently increases for all methods. GP-CCD-MP-DRE remains best: at target dB, the largest tested candidate populations are versus for STMP; at , its advantage over off-grid SBL is dB.

Figure compares GP-CCD-MP-DRE, STMP, and the four baselines for nominal activity probabilities from to , with , , and an SNR of dB.

At fixed , increasing activity raises the number of unknown active coefficients without adding measurements, reducing activity sparsity. GP-CCD-MP-DRE remains most accurate; its gain over STMP grows from dB at to dB at . At the latter point, off-grid SBL slightly surpasses STMP but remains dB behind GP-CCD-MP-DRE. Together with the device-count sweep, this supports the proposed receiver under heavier access loads.

Profile D supplies the training channels. Figure compares profiles D, A, B, and C without retraining. Geometry and receiver settings remain fixed; each of the profile--SNR conditions uses paired scenes.

GP-CCD-MP-DRE outperforms the four sparse-recovery baselines on every evaluated profile. Gains over STMP at dB range from to dB. It remains better on D and C throughout the SNR range, but the ordering changes on A and B: the B curves nearly coincide at dB, and STMP is better by and dB at dB on A and B, respectively. Thus the learned prior transfers beyond profile D, with profile-dependent high-SNR performance.
