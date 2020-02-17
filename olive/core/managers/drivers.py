import importlib
import itertools
import logging
from typing import List, Optional, Tuple

import olive.drivers  # preload
from olive.devices.base import Device, DeviceType
from olive.drivers.base import Driver
from olive.drivers.error import InitializeError, ShutdownError
from olive.utils import Singleton, enumerate_namespace_classes

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
        # list device categories
        self._drivers = {klass: [] for klass in Device.__subclasses__()}
        self.refresh()

    ##

    def refresh(self, force_reload=False):
        """
        Refresh known driver list.

        Args:
            force_reload (bool, optional): force active drivers being reload
        """
        # shutdown active drivers
        active_drivers = self._shutdown_all_drivers(force_reload)
        active_driver_classes = [type(driver) for driver in active_drivers]

        # reload the namespace module
        importlib.reload(olive.drivers)

        # enumerate direct descendents of Driver, and ignore itself
        driver_klasses = enumerate_namespace_classes(
            olive.drivers, lambda x: issubclass(x, Driver) and x != Driver
        )
        logger.info(f"found {len(driver_klasses)} driver(s)")

        logger.info("categorizing drivers by their supported devices")
        for driver_klass in driver_klasses:
            driver_name = driver_klass.__name__

            if driver_klass not in active_driver_classes:
                try:
                    driver = driver_klass()
                    driver.initialize()
                except InitializeError as err:
                    logger.error(
                        f'unable to initialize {driver_name}, due to "{str(err)}"'
                    )
                    continue
            else:
                logger.debug(f'"{driver_name}" is already initialized')

            self._add_driver(driver)

    def query_drivers(self, device_klass: Optional[DeviceType] = None) -> Tuple[Driver]:
        """
        Return drivers of a device category.

        Args:
            device_klass (Device, optional): category of interest, if None, return all
        """
        if device_klass is None:
            return tuple(set(itertools.chain.from_iterable(self._drivers.values())))
        else:
            return tuple(self._drivers[device_klass])

    ##

    def _add_driver(self, driver: Driver):
        """
        Add new driver to book-keep.

        Args:
            driver (Driver): the driver
        """
        device_klasses = driver.enumerate_supported_device_types()
        logger.debug(f"{type(driver).__name__} -> {len(device_klasses)} device type(s)")
        for device_klass in device_klasses:
            logger.debug(f".. {device_klass.__name__}")
            self._drivers[device_klass].append(driver)

    def _shutdown_all_drivers(self, force_shutdown=False) -> List[Driver]:
        """
        Shutdown all enlisted drivers.

        Args:
            force_shutdown (bool, optional): force active drivers being shutdown

        Returns:
            (list of Driver) drivers that are still active
        """
        drivers = self.query_drivers()

        # shutdown all drivers
        active_drivers = []
        for driver in drivers:
            if driver.is_active:
                logger.warning(f"{driver} is still active")
            else:
                try:
                    driver.shudown()
                    continue
                except ShutdownError as err:
                    logger.error(f'{driver} failed to shutdown, due to "{str(err)}"')
            # if we are here, the driver does _not_ shutdown completely
            active_drivers.append(driver)

        if len(active_drivers) > 0:
            if force_shutdown:
                logger.warning("force shutdown ALL active driver(s)")
                # already tried shutdown, so we remove their reference directly
                del active_drivers[:]
            else:
                logger.debug(f"{len(active_drivers)} driver(s) are still active")

        # clear all enlisted drivers
        for drivers in self._drivers.values():
            del drivers[:]

        return active_drivers
