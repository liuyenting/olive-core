import itertools
import logging
from typing import Tuple

from olive.core.utils import Singleton
from olive.devices.base import Device  # TODO fix circular depenency

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
        category = device._determine_category()
        self._devices[category].append(device)
        logger.debug(f"new device {device} registered")

    def unregister(self, device):
        # TODO find parent
        category = device._determine_category()
        try:
            self._devies[category].remove(device)
        except ValueError:
            logger.warning("{device} was ")

    def get_devices(self):
        return self._devices

    @property
    def devices(self) -> Tuple[Device]:
        return tuple(itertools.chain.from_iterable(self._devices.values()))
