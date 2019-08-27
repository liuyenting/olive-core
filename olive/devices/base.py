from abc import ABCMeta, abstractmethod
from collections import deque
from concurrent.futures import ThreadPoolExecutor
import logging
import multiprocessing as mp
from typing import NamedTuple

__all__ = ["Device", "DeviceInfo"]

logger = logging.getLogger(__name__)


class DeviceInfo(NamedTuple):
    #: version of the API
    version: str
    #: vendor of the device
    vendor: str
    #: model of the device
    model: str
    #: serial number
    serial_number: str

    def __repr__(self):
        return f"<{self.vendor}, {self.model}, s/n={self.serial_number}>"


class Device(metaclass=ABCMeta):
    """
    Base class for all device type.
    """

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
    def initialize(self):
        self._register()

    @abstractmethod
    def close(self):
        self._unregister()

    @abstractmethod
    def enumerate_attributes(self):
        pass

    @abstractmethod
    def get_attribute(self, name):
        pass

    @abstractmethod
    def set_attribute(self, name, value):
        pass

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
