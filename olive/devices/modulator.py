from abc import ABCMeta, abstractmethod
from collections import OrderedDict
import logging
from typing import NamedTuple

from olive.devices.base import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator"]

logger = logging.getLogger(__name__)


class Modulator(Device, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        super().__init__()


class ChannelInfo(NamedTuple):
    alias: str
    #: frequency in MHz
    frequency: float
    #: discrete power level
    power: int


class AcustoOpticalModulator(Modulator, metaclass=ABCMeta):
    """
    - channels
        - name
        - freqency
        - power

    - frequency range
    """

    @abstractmethod
    def __init__(self):
        super().__init__()
        self._channels = []

    def get_frequency(self, ch):
        pass

    def set_frequency(self, ch, frequency):
        pass

    def get_power(self, ch):
        pass

    def set_power(self, ch, power):
        pass


class ElectroOpticalModulator(Modulator, metaclass=ABCMeta):
    """
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
