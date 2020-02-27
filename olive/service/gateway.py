import asyncio
import logging
import socket

from olive.core.managers import DeviceManager, DriverManager

__all__ = ["Gateway"]

logger = logging.getLogger(__name__)


class Gateway(object):
    """
    Gateway is the entry point into the OLIVE application from an external client. One can directly interface the acquisition and protocol setups through gateway, locally.

    To access gateway remotely, use `AppController`, which spawns an HTTP server with required endpoints.
    """

    def __init__(self):
        self._driver_manager = DriverManager()
        self._device_manager = DeviceManager()

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

    async def shutdown(self, app):
        # drop all requirements
        self.device_manager.update_requirements(dict())

        # close everything
        await asyncio.gather(
            *[device.close(force=True) for device in self.device_manager.devices],
            return_exceptions=True,
        )

    ##
    # devices - discovery

    def query_hostname(self):
        """Hostname of the host that host this service."""
        return socket.gethostname()

    def list_available_device_classes(self):
        """
        List device classes that have concrete devices.
        """
        pass

    def list_available_devices(self):
        """
        List discovered devices.
        """
        pass

    ##
    # devices - configuration

    ##
    # protocol

    ##
    # acquisition
