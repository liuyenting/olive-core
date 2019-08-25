from abc import ABCMeta, abstractmethod
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
    def _find_root_category(cls):
        """Find root category, since drivers are organized by direct descendent of Device."""

        # TODO
        logger.debug("Device._find_root_category()")
        print(cls.__bases__)
        raise RuntimeError("DEBUG")

    def _register(self):
        """Register the device to DeviceManager."""
        from olive.core import DeviceManager

        DeviceManager().register(self)

    def _unregister(self):
        """Unregister the device from DevieManager."""
        from olive.core import DeviceManager

        DeviceManager().unregister(self)
