from abc import abstractmethod
import itertools
import logging
from typing import get_type_hints, Union

from olive.core import Device
from olive.core.devices import query_device_hierarchy
from olive.core.utils import enumerate_namespace_classes, Singleton
import olive.devices

import olive.drivers

__all__ = ["Driver", "DriverManager", "DriverType"]

logger = logging.getLogger(__name__)


class DriverType(type):
    """All drivers belong to this type."""


class Driver(metaclass=DriverType):
    @abstractmethod
    def __init__(self):
        """Abstract __init__ to prevent instantiation."""

    """
    Driver initialization.
    """

    @abstractmethod
    def initialize(self):
        """Initialize the library. Most notably for singleton instance."""

    @abstractmethod
    def shutdown(self):
        """Cleanup resources allocated by the library."""

    @abstractmethod
    def enumerate_devices(self) -> None:
        """List supported devices."""

    @classmethod
    def enumerate_supported_devices(cls):
        hints = get_type_hints(cls.enumerate_devices)["return"]
        try:
            klasses = hints.__args__
        except AttributeError:
            # not a union
            klasses = [hints]

        # remap to device primitives
        devices = []
        for klass in klasses:
            devices.extend(klass.__bases__)
        return tuple(set(devices) & set(Device.__subclasses__()))

    """
    Driver attributes.
    """

    @abstractmethod
    def enumerate_attributes(self):
        """Get attributes supported by the driver."""

    @abstractmethod
    def get_attribute(self, name):
        """
        Get the value of driver attribute.

        Args:
            name (str): documented attribute name
        """

    @abstractmethod
    def set_attribute(self, name, value):
        """
        Set the value of driver attribute.

        Args:
            name (str): documented attribute name
            value : new value of the specified attribute
        """


class DriverManager(metaclass=Singleton):
    """
    Driver bookkeeping.

    Todo:
        - blacklist
        - driver reload

    Attributes:
        drivers (tuple): a list of known drivers
            This will return everything.
    """

    def __init__(self):
        # populate device categories
        self._drivers = {klass: [] for klass in Device.__subclasses__()}

        self.refresh()

        # TODO isolate list_drivers, use result from _active/_inactive, with category filter

    def refresh(self):
        """Refresh known driver list."""
        # TODO deactivate first

        for drivers in self._drivers.values():
            del drivers[:]

        drivers = enumerate_namespace_classes(
            olive.drivers, lambda x: issubclass(x, Driver)
        )
        logger.info(f"found {len(drivers)} driver(s)")

        logger.info("categorizing drivers to their supported devices...")
        for driver in drivers:
            devices = driver.enumerate_supported_devices()
            logger.debug(f"{driver.__name__} -> {len(devices)} device(s)")
            for device in devices:
                self._drivers[device].append(driver)
                logger.debug(f".. {device.__name__}")

    def query_drivers(self, device):
        return tuple(self._drivers[device])

    ##

    @property
    def drivers(self):
        return tuple(set(itertools.chain.from_iterable(self._drivers.values())))

    """
    Driver classification.
    """

    @staticmethod
    def _inspect_supported_devices(driver):
        devices = []
        for klasses in get_type_hints(driver.enumerate_devices):
            # reverse lookup
            for klass in klasses:
                if klass in Device.__subclasses__():
                    devices.append(klass)

