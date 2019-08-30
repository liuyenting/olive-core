from __future__ import annotations
from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor
import itertools
import logging
import multiprocessing as mp
from typing import Tuple, NamedTuple

from olive.core.utils import Singleton

__all__ = ["Device", "DeviceInfo", "DeviceManager", "DeviceType"]

logger = logging.getLogger(__name__)

#: default thread pool uses 5 times the number of cores
MAX_WORKERS = mp.cpu_count() * 2


class DeviceInfo(NamedTuple):
    version: str
    vendor: str
    model: str
    serial_number: str

    def __repr__(self) -> str:
        if self.version:
            return f"<{self.vendor}, {self.model}, Rev={self.version}, S/N={self.serial_number}>"
        else:
            return f"<{self.vendor}, {self.model}, S/N={self.serial_number}>"


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

        self._is_opened = False

    """
    Device initialization.
    """

    @abstractmethod
    def test_open(self):
        """
        Test open the device.

        Test open is used during enumeration, if mocking is supported, this can avoid full-scale device initialization. This function should be _self-contained_.
        """

    @abstractmethod
    def open(self):
        """
        Open and register the device.

        Note:
            When overloading this function, please remember to use
                super().initialize()
            to ensure this device is registered to the DeviceManager.
        """
        self._is_opened = True
        # TODO registration

    @abstractmethod
    def close(self):
        """
        Close and unregister the device.

        Note:
            When overloading this function, remember to use
                super().close()
            to ensure this device is unregsitered from the DeviceManager.
        """
        # TODO unregistration
        self._is_opened = False

    """
    Device properties.
    """

    @abstractmethod
    def info(self) -> DeviceInfo:
        """Return device info."""

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
        func = self._get_accessor("_get", name)
        return func()

    def set_property(self, name, value):
        """
        Set the value of device property.

        Args:
            name (str): documented property name
        """
        func = self._get_accessor("_set", name)
        func(value)

    def _get_accessor(self, prefix, name):
        try:
            return getattr(self, f"{prefix}_{name}")
        except AttributeError:
            try:
                return getattr(self.parent, f"{prefix}_{name}")
            except AttributeError:
                raise AttributeError(f'unknown property "{name}"')

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

    @property
    def is_opened(self):
        return self._is_opened


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
