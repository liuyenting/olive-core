from abc import abstractmethod
import itertools
import logging
from typing import Tuple

from olive.core.utils import Singleton

__all__ = ["Device", "DeviceManager", "DeviceType"]

logger = logging.getLogger(__name__)


class DeviceType(type):
    """All devices belong to this type."""


class Device(metaclass=DeviceType):
    """
    All primitive device types should inherit from this class.

    Attributes:
        driver : driver that instantiate this device
        parent : parent device
    """

    @abstractmethod
    def __init__(self, driver, parent=None):
        """Abstract __init__ to prevent instantiation."""
        self._driver = driver
        self._parent = parent

    """
    Device initialization.
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

    @abstractmethod
    def get_property(self, name):
        """
        Get the value of device property.

        Args:
            name (str): documented property name
            value : new value of the specified property
        """

    @abstractmethod
    def set_property(self, name, value):
        """
        Set the value of device property.

        Args:
            name (str): documented property name
        """

    @property
    def driver(self):
        return self._driver

    @property
    def parent(self):
        return self._parent


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
