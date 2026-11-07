

Introduction




Sixth-generation (6G) wireless networks are expected to provide ubiquitous connectivity for a massive number of Internet-of-Things (IoT) devices . To serve devices in remote areas with limited terrestrial coverage, low Earth orbit (LEO) satellites complement cellular networks for applications such as smart agriculture and climate monitoring . These power-limited devices transmit short packets sporadically, with only a small fraction active at a given time . In grant-based random access, handshaking before transmission incurs significant signaling overhead, while the long propagation delay of terrestrial-satellite links further increases access latency . Accordingly, grant-free random access (GFRA) allows active devices to transmit pilots and data directly without first obtaining a grant, reducing signaling overhead and access latency in LEO satellite IoT systems .

Supporting GFRA over LEO links requires handling large delays and Doppler shifts caused by long propagation distances and high satellite mobility. The 3rd Generation Partnership Project (3GPP) Release 17 framework addresses these effects through device-side precompensation assisted by the global navigation satellite system (GNSS) . With such precompensation, many existing satellite GFRA schemes assume perfect compensation or small residual delays and Doppler shifts at the receiver . Frequent estimation and compensation increase energy consumption and reduce battery lifetime, making these schemes less suitable for power-limited remote IoT devices . This motivates reducing dependence on GNSS, consistent with the GNSS-independent operation considered in the Release 19 study on satellite access . With reduced reliance on device-side precompensation, the satellite receiver must accommodate large differential delays and Doppler shifts, which can cause severe inter-symbol and inter-carrier interference in conventional orthogonal frequency division multiplexing (OFDM) systems .

Orthogonal time frequency space (OTFS) modulation exploits the quasi-static properties of channels in the delay--Doppler domain to mitigate these effects . In , multi-frame OTFS transmission handles large differential delays and Doppler shifts at the satellite receiver, allowing devices to operate without GNSS assistance or precompensation of these offsets. The effective channel in this scheme is a three-dimensional tensor at each antenna, which requires more observations for channel estimation . However, the two-dimensional transformation in OTFS entails relatively high modulation complexity . Affine frequency division multiplexing (AFDM), based on one-dimensional chirp modulation, offers lower modulation complexity than OTFS while retaining strong Doppler robustness over doubly dispersive channels . With properly designed chirp parameters, AFDM can also achieve full diversity over such channels . This combination of low modulation complexity and full diversity makes AFDM attractive for GFRA with power-limited IoT devices.

To realize the full potential of AFDM-GFRA, accurate joint activity detection and channel estimation (JADCE) is a crucial prerequisite . Existing methods exploit sporadic device activity to formulate JADCE as a compressed sensing (CS) problem and incorporate structured priors to capture channel sparsity . The scheme in  further uses a graph neural network to adaptively learn sparsity patterns, while retaining a predefined delay--Doppler grid for the sparse channel representation. In practical propagation environments, significant power leakage caused by fractional Doppler shifts and fractional time delays can weaken the sparsity of the effective channel matrix . This motivates learning effective-channel priors from data to capture channel structures beyond the assumed sparse representation .

Score-based generative models learn channel priors from samples by estimating the score function of the channel distribution . In , score-based learning is performed directly on the AFDM effective channel to address fractional delay--Doppler off-grid leakage in channel estimation. For massive random access,  proposes a two-stage algorithm that first identifies active devices through a Transformer-based detector and then uses generative diffusion models for joint channel estimation and data detection. Both approaches rely on iterative posterior sampling, which requires repeated score function evaluations and incurs substantial computational cost .

The score-based turbo message passing (STMP) algorithm in  incorporates generative channel priors for JADCE without iterative posterior sampling. Through Tweedie's formulas, separate first- and second-order score networks provide posterior means and variances for single-step minimum mean-squared error (MMSE) denoising under equivalent additive white Gaussian noise (AWGN) observations. However, this AWGN model is justified in the large-system limit with right-rotationally invariant random sensing matrices . In the finite-dimensional, structured multi-frame AFDM system considered here, departures from these conditions may cause a mismatch between denoiser-input errors and the white Gaussian noise used for training. A similar limitation has been highlighted for structured compression matrices in . This mismatch can degrade channel denoising accuracy and, consequently, JADCE performance. Moreover,  computes activity probabilities using Gaussian extrinsic messages obtained after projecting the channel posterior onto a Gaussian distribution. In general, matching posterior means and variances does not preserve the marginal likelihood associated with a non-Gaussian channel prior. Consequently, the resulting activity probabilities can be inaccurate, affecting the channel estimates exchanged with the linear estimation module.

Against this background, we investigate GNSS-independent AFDM-GFRA for LEO satellite IoT systems. Our main contributions are summarized as follows:


 We propose a multi-frame AFDM transmission scheme that accommodates large differential delays and Doppler shifts at the satellite receiver. The scheme reduces modulation complexity through one-dimensional chirp modulation and uses a lower-dimensional effective-channel representation. By exploiting the quasi-static properties of the effective channel over consecutive frames, the scheme provides additional observations for JADCE.

 We learn a score-based generative prior directly from multiantenna AFDM effective-channel samples with fractional delays and Doppler shifts, without imposing sparse or grid-aligned channel assumptions. To address the mismatch between denoiser-input errors and the white Gaussian noise used for training, we train the denoiser using colored Gaussian noise with different covariance matrices.

 We develop a message-passing JADCE receiver for the multi-frame AFDM system. The receiver combines multi-frame linear estimation (MFLE), which suppresses inter-user interference, with generative-prior-aided joint denoising (GPJD), which uses the learned effective-channel prior for MMSE denoising. To reduce errors associated with a Gaussian approximation of the channel posterior, GPJD employs a learned density-ratio estimator to obtain posterior probabilities of activity. The two modules iteratively exchange Gaussian extrinsic messages to perform JADCE. Simulation results demonstrate that the proposed receiver improves activity detection and channel estimation performance compared with STMP across different signal-to-noise ratios and pilot-frame counts.


The remainder of this paper is organized as follows. Section~ presents the system model and the multi-frame AFDM input--output relationship. Sections~-- describe the receiver design, the channel and activity denoisers, and the overall algorithm with its computational complexity analysis, respectively. Section~ presents the simulation results.




System Model




We consider a LEO satellite-enabled grant-free random access system, where AFDM is adopted to mitigate the doubly dispersive effect inherent in terrestrial-satellite links (TSLs) . The system comprises   single-antenna terrestrial devices that communicate with a LEO satellite equipped with a uniform planar array (UPA) consisting of   antennas. During each transmission block, active devices share the same resources for pilot transmission to the satellite. Additionally, we assume that these terrestrial devices operate without GNSS capabilities and do not pre-compensate for delay and Doppler shifts .



Terrestrial-Satellite Link Model



The TSLs experience fast variations due to the high mobility of the LEO satellite. Hence, this time variation and multipath propagation require a doubly dispersive channel model . Moreover, we assume that the terrestrial devices are stationary and all paths from the  th device have a common Doppler shift   . We set   at the beginning of the transmission block. After delay compensation for   at the satellite receiver, the channel impulse response from the  th device to the satellite at time instant   can be represented as

  where  ,   is the number of physical paths,   is the path gain of the  th path, and   is the Dirac delta function. Here   represents the differential delay for the  th path from the  th device to the satellite, where   and   are denoted as propagation delay and common delay, respectively. The common delay corresponds to the propagation time between the satellite and the closest point on Earth within the beam coverage . We assume that the path gains, delays, Doppler shifts, and angles of arrival remain approximately constant within a transmission block.

The array response vector   at the satellite side can be written as    where  ,  ,   is the wavelength, and   is the spacing between adjacent antennas along the  -axis with  . Here   and   are the directional cosines along the z-axis and y-axis, respectively.



Transmission Scheme



In the proposed scheme, each active device transmits pilot symbols over   consecutive AFDM frames within one transmission block. AFDM modulation and demodulation are performed independently for each frame, and the received signals are collected for JADCE. A total of   chirp subcarriers are shared among the devices for pilot transmission . Let   be the pilot symbol transmitted by the  -th device during the  -th AFDM frame on the  -th chirp subcarrier. We construct a pilot vector as  ,  ,  . The pilot symbols are known at the satellite receiver. Let   denote the pilot matrix, with entries  .

We impose the condition that  , where   for all   and   . The design of   is deferred to Section~.

The time-domain transmitted signal is generated through the inverse discrete affine Fourier transform (IDAFT) applied to  , mathematically formulated as 

  where  , and   and   are AFDM modulation parameters. The signal in  can be represented in matrix form as    where   denotes the discrete affine Fourier transform (DAFT) matrix. Here   gives the sampling interval, with   denoting the subcarrier spacing.

Assume that the chirp-periodic prefix (CPP) length is greater than or equal to the maximum differential delay, i.e.,  . The CPP is given by    where   and  . Each AFDM frame spans a duration of  .

To account for fractional delays, we define the transmit waveform for the  th chirp subcarrier at time   as   where   and  . Note that   for  , while   satisfies  for  .

Denote by   the effective channel from the  th device to the satellite during the  th AFDM frame, after removing the CPP and applying the DAFT. For  , the effective channel   can be expressed as   where   and   correspond to the transmitted and received symbols, respectively, and  . For a path with gain  , delay  , and Doppler shift  , the channel response can be expressed in a matrix form as

  where   for   after removing the CPP, and   for frame  . Please refer to Appendix~ for the detailed derivation and the expression for integer  .

Based on  with  , we can derive the effective channel in the  th AFDM frame as   where  . The phase rotation   accumulates across multiple frames, while   remains approximately constant over   consecutive frames. The pilot symbols including this phase rotation are given by  



Problem Formulation



Each device determines whether to access the channel in an independent and identically distributed (i.i.d.) manner. We use an indicator function   to model the device activity as

  Let   represent the probability of a device being active, i.e.,  , where  . As a result, only a small subset of the devices is active in any given transmission block. The activity states are assumed to remain constant during one block transmission. Let  .

After removing the CPP and applying the DAFT, the received signal   during the  th AFDM frame is given by    where   is an AWGN matrix with the elements i.i.d. drawn from  .

We express the received signal   over the   AFDM frames in a more compact form as   where  ,  , and  . The matrices  ,  ,  , and   have the following entries:   Since the   frames share the same  , additional pilot frames provide more observations without increasing the number of channel coefficients to be estimated. Due to the sporadic access of the devices,   exhibits a block-sparsity structure. Specifically, if the  th device is inactive, we have   . For  , the inverse problem in  is underdetermined.

In this paper, we aim to simultaneously detect the active devices and estimate the corresponding channels based on the observation   under a Bayesian inference framework . Power leakage arises from fractional delays and Doppler shifts, which can weaken the sparsity of   . We therefore estimate the full   without imposing channel sparsity. We use the distribution of the training channels as the channel prior  , without factorizing this prior element-wise. We assume that   and   are independent for different values of  , and that   is independent of  . With   and   fixed as in Section~, we factorize the joint posterior distribution according to Bayes' theorem and the conditional independence relationships among the variables, expressed as 

  where   and   denote the  th column of   and  , respectively. Here  ,   enforces  , and  . The MMSE estimate of   and the posterior probability of activity for the  th device are given by

 

