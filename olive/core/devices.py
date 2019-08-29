from __future__ import annotations
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
import itertools
import logging
import multiprocessing as mp
from typing import Tuple

from olive.core.utils import Singleton

__all__ = ["Device", "DeviceManager", "DeviceType"]

logger = logging.getLogger(__name__)

#: default thread pool uses 5 times the number of cores
MAX_WORKERS = mp.cpu_count() * 2


class DeviceType(type):
    """All devices belong to this type."""


class Device(metaclass=DeviceType):
    """
    All primitive device types should inherit from this class.

    Attributes:
        driver : driver that instantiate this device
        parent : parent device

    Note:
        Each device has its own thread executor to prevent external blocking calls
        block the event loop.
    """

    @abstractmethod
    def __init__(self, driver, parent: Device = None):
        """Abstract __init__ to prevent instantiation."""
        self._driver = driver
        self._parent = parent

        self._executor = ThreadPoolExecutor(max_workers=1)

    """
    Device initialization.
    """

    @abstractmethod
    def open(self, test=False):
        """
        Open and register the device.

        Args:
            test (bool): are we testing the device only
                If mocking is supported, enable test to avoid full-scale initialization.
        Note:
            When overloading this function, please remember to use
                super().initialize()
            to ensure this device is registered to the DeviceManager.
        """

    @abstractmethod
    def close(self):
        """
        Close and unregister the device.

        Note:
            When overloading this function, remember to use
                super().close()
            to ensure this device is unregsitered from the DeviceManager.
        """

    """
    Device properties.
    """

    @abstractmethod
    def enumerate_properties(self):
        """Get properties supported by the device."""

    def get_property(self, name):
        """
        Get the value of device property.

        Args:
            name (str): documented property name
            value : new value of the specified property
        """
        func = getattr(self, f"_get_{name}")
        return func()

    def set_property(self, name, value):
        """
        Set the value of device property.

        Args:
            name (str): documented property name
        """
        setattr(self, f"_set_{name}")

    """
    Driver-device associations.
    """

    @property
    def driver(self):
        return self._driver

    @property
    def parent(self) -> Device:
        return self._parent

    """
    Exceution.
    """

    @property
    def executor(self):
        return self._executor


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        # populate categories
        self._devices = {klass: [] for klass in Device.__subclasses__()}

    def register(self, device):
        # FIXME devic registration is completely detached right now
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
