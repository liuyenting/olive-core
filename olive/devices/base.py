from abc import ABCMeta, abstractmethod
from collections import deque
from  concurrent.futures import ThreadPoolExecutor
import logging
import multiprocessing as mp

__all__ = ["Device"]

logger = logging.getLogger(__name__)

#: default thread pool uses 5 times the number of cores
MAX_WORKERS = mp.cpu_count() * 2


class Device(metaclass=ABCMeta):
    """
    Base class for all device type.
    """

    executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    @abstractmethod
    def __init__(self, nthreads=1):
        """
        Note:
            Prevent user from instantiation.
        """

    @classmethod
    @abstractmethod
    def enumerate_devices(cls):
        """List supported hardwares."""

    @abstractmethod
    async def initialize(self):
        """
        Initialize and register the device.

        Note:
            When overloading this function, please remember to use
                super().initialize()
            to ensure this device is registered to the DeviceManager.
        """
        self._register()

    @abstractmethod
    async def close(self):
        """
        Close and unregister the device.

        Note:
            When overloading this function, remember to use
                super().close()
            to ensure this device is unregsitered from the DeviceManager.
        """
        self._unregister()

    @abstractmethod
    async def enumerate_attributes(self):
        """Get attributes supported by the device."""

    @abstractmethod
    async def get_attribute(self, name):
        """
        Get the value of device attributes.

        Args:
            name (str): documented attribute name
        """

    @abstractmethod
    async def set_attribute(self, name, value):
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
