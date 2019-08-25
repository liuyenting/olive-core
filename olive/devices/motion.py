import logging

from olive.devices.base import Device

__all__ = ["Galvo"]

logger = logging.getLogger(__name__)


class Galvo(Device):
    """
    A beam steering device.
    """

    def __init__(self):
        pass
