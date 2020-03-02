import asyncio
import logging
import socket
from typing import Union
from uuid import uuid1

from bidict import bidict

from olive.core.managers import DeviceManager, DriverManager

__all__ = ["Gateway"]

logger = logging.getLogger(__name__)


class Gateway(object):
    """
    Gateway is the entry point into the OLIVE application. One can directly interface
    the acquisition and protocol setups through gateway locally.
    """

    def __init__(self):
        self._driver_manager = DriverManager()
        self._device_manager = DeviceManager()

        self._objects = bidict()  # object -> uuid

    ##

    @property
    def driver_manager(self):
        return self._driver_manager

    @property
    def device_manager(self):
        return self._device_manager

    ##
    # gateway initialize/shutdown

    async def initialize(self, app):
        # driver manager must refresh _at least once_ during startup
        await self.driver_manager.refresh()

        # monitor available devices
        drivers = self.driver_manager.query_drivers()
        results = await asyncio.gather(
            *[driver.enumerate_devices() for driver in drivers], return_exceptions=True
        )

        # register devices in DeviceManger
        for devices in results:
            for device in devices:
                self.device_manager.register(device)
        logger.debug(f"{len(self.device_manager._tasks)} device(s) to register")
        await self.device_manager.wait_ready()

        logger.info("gateway initialized")

    async def shutdown(self, app):
        logger.info("gateway shutdown in-progress")

        # drop all requirements
        self.device_manager.update_requirements(dict())

        # close everything
        await asyncio.gather(
            *[device.close(force=True) for device in self.device_manager.devices],
            return_exceptions=True,
        )

    ##
    # object access

    def translate(self, k: Union[object, int]) -> Union[object, int]:
        """
        Translate objects to and from a UUID.

        Args:
            k (object or int): key to translate

        Returns:
            (int or object): translated result
        """
        lut = self._objects.inv if isinstance(k, str) else self._objects
        try:
            return lut[k]
        except KeyError:
            if isinstance(k, str):
                # invalid uuid
                raise

            # new object, generate a UUID and save it
            uuid = uuid1().int >> 64
            self._objects[k] = uuid
            return uuid

    def cleanup_object_lut(self):
        """Cleanup the forward/reverse lookup cache."""
        # TODO how to clean up the lookup cache?
        pass

    ##
    # devices - discovery

    def get_hostname(self):
        """Hostname of the host that host this service."""
        return socket.gethostname()

    def get_available_devices(self):
        """Get list of discovered devices in their UUID."""
        uuid = [self.translate(device) for device in self.device_manager.devices]
        return uuid

    def get_available_device_classes(self):
        """List device classes that have concrete devices."""
        # TODO rebuild available classes from stored device list in device manager
        pass

    ##
    # devices - configuration

    ##
    # protocol

    ##
    # acquisition
