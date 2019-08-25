from abc import ABCMeta, abstractmethod
import logging
from typing import ByteString
from uuid import uuid4

all = ["Device"]

logger = logging.getLogger(__name__)


class Device(metaclass=ABCMeta):
    """
    Base class for all device type.
    """

    @abstractmethod
    def __init__(self):
        """
        Note:
            Prevent user from instantiation.
        """
        self._uuid = None

    @classmethod
    @abstractmethod
    def discover(cls):
        """List supported hardwares."""

    @abstractmethod
    def initialize(self):
        """
        Initialize and register the device.
        
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

    @abstractmethod
    def enumerate_attributes(self):
        """Get attributes supported by the device."""

    @abstractmethod
    def get_attribute(self, name):
        """
        Get the value of device attributes.

        Args:
            name (str): documented attribute name
        """

    @abstractmethod
    def set_attribute(self, name, value):
        """
        Set the value of device attributes.

        Args:
            name (str): documented attribute name
            value : new value of the specified attribute
        """

    @property
    def uuid(self) -> ByteString:
        return self._uuid

    def _register(self):
        """Register the device to DeviceManager."""
        self._uuid = uuid4().bytes

    def _unregister(self):
        """Unregister the device from DevieManager."""
        self._uuid = None
