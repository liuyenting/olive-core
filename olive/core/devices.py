import itertools
import logging
from typing import Tuple

from olive.core.utils import Singleton
from olive.devices.base import Device

__all__ = ["DeviceManager"]

logger = logging.getLogger(__name__)


class Device(type):
    """All devices belong to this type."""


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        # populate categories
        self._devices = {klass: [] for klass in Device.__subclasses__()}

    def register(self, device):
        category = device._determine_category()
        self._devices[category].append(device)
        logger.debug(f"new device {device} registered")

    def unregister(self, device):
        category = device._determine_category()
        self._devices[category].remove(device)
        logger.debug(f"{device} unregistered")

    def get_devices(self):
        return self._devices

    @property
    def devices(self) -> Tuple[Device]:
        return tuple(set(itertools.chain.from_iterable(self._devices.values())))
