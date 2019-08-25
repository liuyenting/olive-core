from abc import ABCMeta, abstractmethod
from collections import deque
import logging

__all__ = ["Device"]

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
        self._register()

    @abstractmethod
    def close(self):
        """
        Close and unregister the device.

        Note:
            When overloading this function, remember to use
                super().close()
            to ensure this device is unregsitered from the DeviceManager.
        """
        self._unregister()

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

    @classmethod
    def _determine_category(cls):
        """Determine device category, since drivers are organized by direct descendent of Device."""
        visited, queue = set(), deque([cls])
        while queue:
            klass = queue.popleft()
            for parent in klass.__bases__:
                if parent == Device:
                    # klass is a primitive device type
                    logger.debug(f"{cls} is {klass}")
                    return klass
                elif parent not in visited:
                    # skip over cyclic dependency
                    visited.add(parent)
                    queue.append(parent)
        raise RuntimeError(f"{cls} does not fall under known categories")

    def _register(self):
        """Register the device to DeviceManager."""
        from olive.core import DeviceManager

        DeviceManager().register(self)

    def _unregister(self):
        """Unregister the device from DevieManager."""
        from olive.core import DeviceManager

        DeviceManager().unregister(self)
