from abc import ABCMeta, abstractmethod
import logging
from typing import NamedTuple

from olive.core import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator"]

logger = logging.getLogger(__name__)


class Modulator(Device):
    pass


class ChannelInfo(NamedTuple):
    alias: str
    #: frequency in MHz
    frequency: float
    #: discrete power level
    power: int


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
    def __init__(self, driver):
        super().__init__(driver)
        self._channels = []

    def get_frequency(self, channel):
        pass

    def set_frequency(self, channel, frequency):
        pass

    def get_power(self, channel):
        pass

    def set_power(self, channel, power):
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

    @abstractmethod
    def __init__(self):
        super().__init__()
