from abc import ABC, abstractmethod


class Oscillator(ABC):
    def __init__(
        self, freq=440, phase=0, amp=1, sample_rate=44_100, wave_range=(-1, 1)
    ):
        self._freq = freq
        self._amp = amp
        self._phase = phase
        self._sample_rate = sample_rate
        self._wave_range = wave_range

        # Properties that will be changed
        self._f = freq
        self._a = amp
        self._p = phase

    @property
    def init_freq(self):
        return self._freq

    @property
    def init_amp(self):
        return self._amp

    @property
    def init_phase(self):
        return self._phase

    @property
    def freq(self):
        return self._f

    @freq.setter
    def freq(self, value):
        self._f = value
        self._post_freq_set()

    @property
    def amp(self):
        return self._a

    @amp.setter
    def amp(self, value):
        self._a = value
        self._post_amp_set()

    @property
    def phase(self):
        return self._p

    @phase.setter
    def phase(self, value):
        self._p = value
        self._post_phase_set()

    def _post_freq_set(self):
        pass

    def _post_amp_set(self):
        pass

    def _post_phase_set(self):
        pass

    @abstractmethod
    def _initialize_osc(self):
        pass

    @staticmethod
    def squish_val(val, min_val=0, max_val=1):
        return (((val + 1) / 2) * (max_val - min_val)) + min_val

    @abstractmethod
    def __next__(self):
        return None

    def __iter__(self):
        self.freq = self._freq
        self.phase = self._phase
        self.amp = self._amp
        self._initialize_osc()
        return self
