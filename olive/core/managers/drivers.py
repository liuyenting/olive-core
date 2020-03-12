import importlib
import itertools
import logging
from typing import List, Optional, Tuple
import asyncio

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
    """

    def __init__(self):
        # organize drivers by their supported device classes
        self._drivers = {klass: [] for klass in Device.__subclasses__()}

    ##

    async def refresh(self, force_reload=False):
        """
        Refresh known driver list.

        Args:
            force_reload (bool, optional): force active drivers being reload
        """
        # shutdown active drivers
        active_drivers = await self._shutdown_all_drivers(force_reload)
        active_driver_classes = [type(driver) for driver in active_drivers]

        # reload the namespace module
        importlib.reload(olive.drivers)

        # enumerate direct descendents of Driver, and ignore itself
        driver_klasses = enumerate_namespace_classes(
            olive.drivers, lambda x: issubclass(x, Driver) and x != Driver
        )
        logger.info(f"found {len(driver_klasses)} driver(s)")

        logger.info("categorizing drivers by their supported devices")
        drivers = []
        for driver_klass in driver_klasses:
            driver_name = driver_klass.__name__

            if driver_klass not in active_driver_classes:
                driver = driver_klass()
                drivers.append(driver)
            else:
                logger.debug(f'"{driver_name}" is already initialized')

        logger.info(f"initializing {len(drivers)} driver(s)")
        init_tasks = [driver.initialize() for driver in drivers]
        results = await asyncio.gather(*init_tasks, return_exceptions=True)

        for driver, result in zip(drivers, results):
            if result is None:
                self._add_driver(driver)
            else:
                try:
                    raise result
                except InitializeError as err:
                    # gracefully logged and ignored
                    driver_name = type(driver).__name__
                    logger.error(
                        f'unable to initialize {driver_name}, due to "{str(err)}"'
                    )

    def query_drivers(self, device_klass: Optional[DeviceType] = None) -> Tuple[Driver]:
        """
        Return drivers that support the specified device class.

        Args:
            device_klass (Device, optional): class of interest, if `None`, return all
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

    async def _shutdown_all_drivers(self, force=False) -> List[Driver]:
        """
        Shutdown all enlisted drivers.

        Args:
            force (bool, optional): force drivers that have devices actively in-use to
                shutdown

        Returns:
            (list of Driver) drivers that are still active
        """
        drivers = self.query_drivers()

        # shutdown drivers
        shutdown_tasks = [driver.shutdown() for driver in drivers]
        results = await asyncio.gather(*shutdown_tasks, return_exceptions=True)

        active_drivers = []
        for driver, result in zip(drivers, results):
            if result is not None:
                # something really wrong, typically, runtime error
                logger.critical(result)
            elif driver.is_active:
                logger.warning(f"{driver} is still active")
                active_drivers.append(driver)
        logger.info(f"{len(active_drivers)} driver(s) are still active")

        if len(active_drivers) > 0:
            if force:
                logger.warning("force shutdown remaining active driver(s)")
                # already tried shutdown, so we delete their reference directly
                del active_drivers[:]

        # clear all internally enlisted drivers
        for drivers in self._drivers.values():
            del drivers[:]

        return active_drivers
