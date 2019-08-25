import itertools
import logging
from typing import Tuple

from olive.core.utils import Singleton
from olive.devices.base import Device

__all__ = ["DeviceManager"]

logger = logging.getLogger(__name__)


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        # populate categories
        self._devices = {klass: [] for klass in Device.__subclasses__()}

    def register(self, device):
        klass = device._determine_primtives()
        for _klass in klass:
            self._devices[_klass].append(device)
        logger.debug(f"new device {device} registered")

    def unregister(self, device):
        klass = device._determine_primtives()
        for _klass in klass:
            self._devices[_klass].remove(device)
        logger.debug(f"{device} unregistered")

    def get_devices(self):
        return self._devices

    @property
    def devices(self) -> Tuple[Device]:
        return tuple(set(itertools.chain.from_iterable(self._devices.values())))
