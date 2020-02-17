from abc import abstractmethod
from typing import NamedTuple

from .base import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator"]


class ChannelInfo(NamedTuple):
    alias: str
    #: frequency in MHz
    frequency: float
    #: discrete power level
    power: int


class Modulator(Device):
    @abstractmethod
    def is_enabled(self):
        """Is the chanel enabled?"""

    @abstractmethod
    def enable(self, force=True):
        """Enable a channel."""

    @abstractmethod
    def disable(self, force=True):
        """Disable a channel."""


class AcustoOpticalModulator(Modulator, Device):
    """
    This primitive device refers to devices using acousto-optic effect to diffract and
    shift the frequency of light using sound waves at radio frequency.

    An oscillating (frequency) electric signal drives (power) the piezoelectric
    transducer to vibrate, which creates sound waves in the material. The moving
    periodic planes of expansion and compression change the refraction index.

    - channels
        - name
        - freqency
        - power

    - frequency range
    """

    @abstractmethod
    def get_frequency_range(self, channel):
        pass

    @abstractmethod
    def get_frequency(self, channel):
        pass

    @abstractmethod
    def set_frequency(self, channel, frequency, force=False):
        pass

    @abstractmethod
    def get_power_range(self, channel):
        pass

    @abstractmethod
    def get_power(self, channel):
        pass

    @abstractmethod
    def set_power(self, channel, power, force=False):
        pass


class ElectroOpticalModulator(Modulator, Device):
    """
    This primitive device refers to devices in which a signal-controlled element
    exhibiting an electro-optic effect is used to modulate a beam of light.

    The elector-optic effect is the change in the refractive index of a material
    resulting from the application of a DC (bias) or low-frequency (gain) electric
    field.

    - channel (1)
        - gain
        - bias

    - power range
        - gain
            - min
            - max
        - bias
            - min
            - max
    """
