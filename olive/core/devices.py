from collections import defaultdict
import logging
from uuid import uuid4 as uuid

from olive.core.utils import Singleton


__all__ = ["DeviceManager"]

logger = logging.getLogger(__name__)


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        logger.debug("Device Manager initiated")

        self._devices = defaultdict(list)

    def add_device(self, device):
        self._devices[uuid().hex] = device

    def add_driver(self, a, b):
        pass  # TODO remove this function and depenency in olive.devices.base.Device

    def get_devices(self):
        return self._devices
