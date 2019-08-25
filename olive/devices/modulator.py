from abc import ABCMeta, abstractmethod
import logging

from .base import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator"]

logger = logging.getLogger(__name__)


class Modulator(Device, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        super().__init__()


class AcustoOpticalModulator(Modulator, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        super().__init__()

    # TODO define channels


class ElectroOpticalModulator(Modulator, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        super().__init__()
