from abc import abstractmethod
import importlib
import inspect
import itertools
import logging
from typing import get_type_hints

from olive.core import Device
from olive.core.utils import enumerate_namespace_subclass, Singleton
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
        drivers (dict): list of known drivers
            This will return everything.
    """

    def __init__(self, blacklist=[]):
        # populate categories
        self._drivers = {klass: [] for klass in Driver.__subclasses__()}

        self.refresh()

        # TODO isolate list_drivers, use result from _active/_inactive, with category filter

    def refresh(self):
        """Refresh known driver list."""
        # TODO deactivate first

        for drivers in self._drivers.values():
            del drivers[:]

        for driver in enumerate_namespace_subclass(olive.drivers, Driver):
            category = driver._determine_category()
            self._drivers[category].append(driver)

    def query_devices(self, category):
        return tuple(self._drivers[category])

    @property
    def drivers(self):
        return tuple(set(itertools.chain.from_iterable(self._drivers.values())))

    """
    Driver classification.
    """

    @staticmethod
    def _supported_devices(driver):
        devices = []
        for klasses in get_type_hints(driver.enumerate_devices):
            # reverse lookup
            for klass in klasses:
                if klass in Device.__subclasses__():
                    devices.append(klass)

