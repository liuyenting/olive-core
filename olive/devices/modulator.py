from abc import ABCMeta, abstractmethod
import logging

from .base import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator"]

logger = logging.getLogger(__name__)


class Modulator(Device, metaclass=ABCMeta):
    pass


class AcustoOpticalModulator(Modulator, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        pass

    #TODO define channels


class ElectroOpticalModulator(Modulator, metaclass=ABCMeta):
    pass
