from abc import ABCMeta
import logging

from .base import Device

__all__ = ["AcustoOpticalModulator", "ElectroOpticalModulator"]

logger = logging.getLogger(__name__)


class Modulator(Device, metaclass=ABCMeta):
    pass


class AcustoOpticalModulator(Modulator, metaclass=ABCMeta):
    pass


class ElectroOpticalModulator(Modulator, metaclass=ABCMeta):
    pass
