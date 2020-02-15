import itertools
import logging
from typing import get_type_hints

from olive.devices.base import Device
from olive.drivers.base import Driver
from olive.utils import enumerate_namespace_classes, Singleton

import olive.drivers  # preload

__all__ = ["DriverManager"]

logger = logging.getLogger(__name__)


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
        # deactivate all
        for drivers in self._drivers.values():
            for driver in drivers:
                driver.shutdown()
            del drivers[:]

        drivers = enumerate_namespace_classes(
            olive.drivers, lambda x: issubclass(x, Driver)
        )
        logger.info(f"found {len(drivers)} driver(s)")

        logger.info("categorizing drivers to their supported devices...")
        for driver in drivers:
            driver.initialize()
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

