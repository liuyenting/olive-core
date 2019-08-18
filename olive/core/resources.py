from collections import defaultdict
import logging
from uuid import uuid4 as uuid

__all__ = ["DeviceManager", "BufferManager"]

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        logger.debug("Device Manager initiated")

        self._devices = defaultdict(list)
        self._drivers = defaultdict(list)

    def add_driver(self, category, driver):
        self._drivers[category].append(driver)

    def add_device(self, device):
        self._devices[uuid().hex] = device

    def get_drivers(self):
        return self._drivers

    def get_devices(self):
        return self._devices


class BufferManager(metaclass=Singleton):
    def __init__(self):
        pass
