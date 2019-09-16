from abc import abstractmethod
import logging

from olive.core import Device

__all__ = []

logger = logging.getLogger(__name__)


class LightSource(Device):
    """
    Source of light.
    """


class Laser(LightSource, Device):
    """
    A device that emits light through a process of optical amplification based on the
    stimulated emission of electromagnetic radiation.
    """
