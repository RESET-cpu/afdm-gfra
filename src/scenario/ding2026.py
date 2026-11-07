"""Ding (2026) Eqs. (1)--(9): one AFDM frame and its pilot submatrix.

The reported Fig. 3 parameters are retained. N, chirps, pilot distribution,
and the choice/scaling of the 3GPP three-tap profile are declared settings:
the accepted manuscript does not specify them. This is a reimplementation,
not the authors' simulator. It does not import/change the project's physics.
"""
from dataclasses import asdict
from dataclasses import dataclass
from functools import lru_cache

import numpy as np


MODEL_VERSION = 'ding2026_pilot_equations_v1'
PAPER_SHA256 = '22dceda0036c892f44e961ce9ab6d094930e610befe0d51c18c3357aa1890ec5'
# 3GPP TR 38.811, Table 6.9.2-1. Source read: ATIS V15.3.0, p.89.
# Ding cites V15.4.0, but does not identify its selected NTN channel profile.
TDL_A_DELAYS = (0., 1.0811, 2.8416)
TDL_A_POWER_DB = (0., -4.675, -6.482)


@dataclass(frozen=True)
class DingSimulationSettings:
    users: int = 100
    antennas: int = 4
    subcarriers: int = 128
    pilot_length: int = 50
    delay_max: int = 2
    delay_intervals: int = 2
    doppler_intervals: int = 4
    doppler_max_hz: float = 30000.
    subcarrier_spacing_hz: float = 15000.
    carrier_hz: float = 4e9
    activity_probability: float = .1
    fractional_doppler_guard: int = 0
    c2: float = float(np.sqrt(2.)/(10*128**2))
    require_active_user: bool = True

    def __post_init__(self):
        ints = (self.users, self.antennas, self.subcarriers, self.pilot_length,
                self.delay_max, self.delay_intervals, self.doppler_intervals)
        if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in ints):
            raise ValueError('positive integer Ding dimensions and grid intervals required')
        if (not isinstance(self.fractional_doppler_guard, int)
                or isinstance(self.fractional_doppler_guard, bool)
                or self.fractional_doppler_guard < 0
                or not all(np.isfinite(v) and v > 0 for v in
                    (self.doppler_max_hz, self.subcarrier_spacing_hz, self.carrier_hz))
                or not np.isfinite(self.c2)
                or not np.isfinite(self.activity_probability)
                or not 0 < self.activity_probability < 1
                or not isinstance(self.require_active_user, bool)):
            raise ValueError('valid finite Ding physical and activity settings required')
        if self.pilot_end+self.guard_length > self.subcarriers:
            raise ValueError('the pilot and both guards must fit in the AFDM frame')
        delay, doppler = grid_axes(self)
        if (not np.allclose(delay, np.rint(delay), atol=1e-12, rtol=0)
                or not np.allclose(doppler/self.subcarrier_spacing_hz,
                                   np.rint(doppler/self.subcarrier_spacing_hz), atol=1e-12, rtol=0)):
            raise ValueError('this original-scene entry requires integer delay/Doppler grids')

    @property
    def alpha_max(self):
        return int(np.ceil(self.doppler_max_hz/self.subcarrier_spacing_hz))

    @property
    def guard_length(self):
        # Ding Eq. (6) Q, as printed; it is not the project's frame count Q.
        return (self.delay_max+1)*(2*(self.alpha_max+self.fractional_doppler_guard)+1)

    @property
    def pilot_end(self):
        return self.guard_length+self.pilot_length

    @property
    def observation_length(self):
        return self.pilot_end

    @property
    def c1(self):
        # Bemani (2023), III-E Eq. (42), integer Doppler choice.
        return (2*(self.alpha_max+self.fractional_doppler_guard)+1)/(2*self.subcarriers)

    @property
    def grid_shape(self):
        return self.delay_intervals+1, self.doppler_intervals+1


def grid_axes(settings):
    return (np.linspace(0., settings.delay_max, settings.delay_intervals+1),
            np.linspace(-settings.doppler_max_hz, settings.doppler_max_hz,
                        settings.doppler_intervals+1))


def grid_coordinates(settings):
    delay, doppler = grid_axes(settings)
    return np.array([(d, v) for d in delay for v in doppler])


def pilot_indices(settings):
    return np.arange(settings.guard_length, settings.pilot_end)


def observation_indices(settings):
    start = settings.alpha_max+settings.fractional_doppler_guard
    return np.arange(start, start+settings.observation_length)


def path_matrix(settings, delay_samples, doppler_hz):
    """Integer-grid AFDM path matrix, independently expanded from Eq. (1).

    Ding uses exp(-j*2*pi*nu*n/N). An input bin m arrives at bin
    p=(m-nu-2*N*c1*d) mod N with the phase below. CPP extension makes
    the same expression valid when n-d is negative. No channel gain here.
    """
    n = settings.subcarriers
    d = float(delay_samples)
    alpha = float(doppler_hz)/settings.subcarrier_spacing_hz
    if not np.isfinite([d, alpha]).all() or abs(d-round(d)) > 1e-12 or abs(alpha-round(alpha)) > 1e-12:
        raise ValueError('integer delay and normalized Doppler required')
    m = np.arange(n)
    p = (m-int(round(alpha))-int(round(2*n*settings.c1))*int(round(d))) % n
    phase = settings.c1*d*d-m*d/n+settings.c2*(m*m-p*p)
    matrix = np.zeros((n, n), complex)
    matrix[p, m] = np.exp(2j*np.pi*phase)
    return matrix


@lru_cache(maxsize=8)
def pilot_path_matrices(settings):
    ir, ip = observation_indices(settings), pilot_indices(settings)
    matrices = np.stack([path_matrix(settings, d, v)[np.ix_(ir, ip)]
                         for d, v in grid_coordinates(settings)])
    matrices.setflags(write=False)
    return matrices


def design_from_pilots(pilots, settings):
    p = np.asarray(pilots)
    if p.shape != (settings.users, settings.pilot_length) or not np.isfinite(p).all():
        raise ValueError('finite pilot[users,pilot_length] required')
    # Order (user, delay, Doppler), with antenna vectors in each Z row.
    return np.einsum('grn,kn->rkg', pilot_path_matrices(settings), p,
                     optimize=True).reshape(settings.observation_length, -1)


def direct_full_frame(settings, symbols, coefficients):
    """Independent IDAFT, real-time delay/CPP and Doppler, then DAFT.

    The signal includes actual data outside both pilot guards. It never
    calls path_matrix or multiplies the compressed pilot dictionary.
    """
    n = settings.subcarriers
    x, z = np.asarray(symbols, complex), np.asarray(coefficients, complex)
    nodes = int(np.prod(settings.grid_shape))
    if x.shape != (settings.users, n) or z.shape != (settings.users*nodes, settings.antennas):
        raise ValueError('compatible full-frame symbols and coefficient rows required')
    time = np.arange(n)
    idaft = np.exp(2j*np.pi*(settings.c1*time[:, None]**2
        + settings.c2*time[None, :]**2+time[:, None]*time[None, :]/n))/np.sqrt(n)
    transmitted = x@idaft.T
    received = np.zeros((n, settings.antennas), complex)
    z = z.reshape(settings.users, nodes, settings.antennas)
    for g, (d, v) in enumerate(grid_coordinates(settings)):
        logical = time-int(d)
        remainder = logical % n
        cpp = np.exp(2j*np.pi*settings.c1*(logical**2-remainder**2))
        doppler = np.exp(-2j*np.pi*(v/settings.subcarrier_spacing_hz)*time/n)
        delayed = transmitted[:, remainder]*cpp[None, :]*doppler[None, :]
        received += delayed.T@z[:, g, :]
    return idaft.conj().T@received


def generate_case(seed, snr_db, settings=None, *, include_full_frame=False):
    """Return public input, private coefficients/activity, and provenance.

    Missing-source choices: unit QPSK pilots/data; compensated path loss;
    NTN-TDL-A powers with scaled/quantized delays 0,1,2; a common on-grid
    residual Doppler per device (stationary UE); independent CN antenna
    gains. The finite Z grid and reported paper dimensions are exact.
    """
    s = settings or DingSimulationSettings()
    if not np.isfinite(snr_db):
        raise ValueError('finite SNR required')
    streams = [np.random.default_rng(v) for v in np.random.SeedSequence(int(seed)).spawn(5)]
    activity_rng, path_rng, pilot_rng, noise_rng, data_rng = streams
    activity = activity_rng.random(s.users) < s.activity_probability
    draws = 1
    while s.require_active_user and not activity.any():
        activity = activity_rng.random(s.users) < s.activity_probability
        draws += 1
    pilots = ((2*pilot_rng.integers(0, 2, (s.users, s.pilot_length))-1)
              + 1j*(2*pilot_rng.integers(0, 2, (s.users, s.pilot_length))-1))/np.sqrt(2.)
    delay_axis, doppler_axis = grid_axes(s)
    scaled_delays = np.asarray(TDL_A_DELAYS)*s.delay_max/TDL_A_DELAYS[-1]
    delay_rows = np.abs(delay_axis[:, None]-scaled_delays[None, :]).argmin(axis=0)
    frequencies = path_rng.integers(0, len(doppler_axis), size=s.users)
    powers = 10.**(np.asarray(TDL_A_POWER_DB)/10.)
    gains = (path_rng.normal(size=(s.users, 3, s.antennas))
             + 1j*path_rng.normal(size=(s.users, 3, s.antennas)))*np.sqrt(powers[None, :, None]/2.)
    z = np.zeros((s.users, int(np.prod(s.grid_shape)), s.antennas), complex)
    support = np.zeros(z.shape[:2], bool)
    for k in range(s.users):
        for p, d in enumerate(delay_rows):
            g = int(d)*len(doppler_axis)+int(frequencies[k])
            if activity[k]:
                z[k, g] += gains[k, p]
                support[k, g] = True
    z = z.reshape(-1, s.antennas)
    design = design_from_pilots(pilots, s)
    clean = design@z
    clean_power = float(np.mean(abs(clean)**2))
    # Nonempty settings use the printed SNR exactly. An allowed empty case
    # retains a positive predeclared expected-power noise convention.
    reference_power = (s.users*s.activity_probability*s.pilot_length*powers.sum()
                       /s.observation_length)
    noise = (clean_power if clean_power > 0 else reference_power)*10.**(-float(snr_db)/10.)
    standard_noise = (noise_rng.normal(size=clean.shape)+1j*noise_rng.normal(size=clean.shape))/np.sqrt(2.)
    public = dict(observation=clean+np.sqrt(noise)*standard_noise,
                  design=design, noise_variance=np.asarray(noise), pilots=pilots)
    truth = dict(coefficients=z, activity=activity.astype(np.int8), support=support.reshape(-1), clean=clean)
    metadata = dict(generator_version=MODEL_VERSION, seed=int(seed), snr_db=float(snr_db),
        settings=asdict(s), grid_shape=list(s.grid_shape), observations=s.observation_length,
        guard_length=s.guard_length, c1=s.c1, active_users=int(activity.sum()),
        activity_draws=draws, require_active_user=s.require_active_user,
        channel_profile='NTN-TDL-A; selected implementation profile, unspecified by Ding',
        channel_source='3GPP TR38.811 Table6.9.2-1, ATIS V15.3.0 printed p.89',
        scaled_delay_samples=scaled_delays.tolist(), quantized_delay_samples=delay_axis[delay_rows].tolist(),
        powers_db=list(TDL_A_POWER_DB), compensated_path_loss=True,
        antenna_fading='independent proper complex Gaussian with shared path support',
        residual_doppler='one uniform integer-grid residual per device, common to taps',
        input_scope='Y, known pilot dictionary, supplied noise; no support/coefficient/activity truth',
        empty_scene_noise_fallback=bool(clean_power == 0),
        paper_parameter_reimplementation=True, author_code=False)
    if include_full_frame:
        symbols = ((2*data_rng.integers(0, 2, (s.users, s.subcarriers))-1)
                   + 1j*(2*data_rng.integers(0, 2, (s.users, s.subcarriers))-1))/np.sqrt(2.)
        symbols[:, :s.guard_length] = 0
        symbols[:, s.guard_length:s.pilot_end] = pilots
        symbols[:, s.pilot_end:s.pilot_end+s.guard_length] = 0
        truth['full_symbols'] = symbols
        truth['full_clean_observation'] = direct_full_frame(s, symbols, z)
    return public, truth, metadata
