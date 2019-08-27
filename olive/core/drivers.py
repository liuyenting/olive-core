from abc import abstractmethod
import importlib
import inspect
import itertools
import logging
import pkgutil
from typing import get_type_hints

from olive.core import Device
from olive.core.utils import Singleton
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
        pass

    @abstractmethod
    def shutdown(self):
        pass

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

        for driver in DriverManager._enumerate_drivers():
            category = driver._determine_category()
            self._drivers[category].append(driver)

    def query_devices(self, category):
        return tuple(self._drivers[category])

    @property
    def drivers(self):
        return tuple(set(itertools.chain.from_iterable(self._drivers.values())))

    """
    Namespace deep scan.
    """

    @staticmethod
    def _iter_namespace(pkg_name):
        """
        Iterate over a namespace package.

        Args:
            pkg_name (type): namespace package to iterate over

        Returns:
            (tuple): tuple containing
                finder (FileFinder): module location
                name (str): fully qualified name of the found item
                is_pkg (bool): whether the found path is a package
        """
        return pkgutil.iter_modules(pkg_name.__path__, pkg_name.__name__ + ".")

    @staticmethod
    def _enumerate_drivers():
        """
        Iterate over the driver namespace and list out all potential drivers.

        Args:
            category (Device): device type class

        Returns:
            (list): a list of drivers
        """
        drv = []
        drv_pkgs = DriverManager._iter_namespace(olive.drivers)
        for _, name, is_pkg in drv_pkgs:
            drv_pkg = importlib.import_module(name)
            _drv = []
            for _, klass in inspect.getmembers(drv_pkg, inspect.isclass):
                if issubclass(klass, Driver):
                    _drv.append(klass)
            logger.debug(f'"{name}" contains {len(_drv)} driver(s)')
            for klass in _drv:
                logger.debug(f".. {klass.__name__}")
            drv.extend(_drv)
        logger.info(f"{len(drv)} driver(s) loaded")
        return drv

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

