import asyncio
import logging
from typing import Iterable

from serial_asyncio import open_serial_connection

from olive.devices.base import Device
from olive.drivers.base import Driver
from olive.drivers.utils import SerialPortManager

__all__ = ["Sutter"]

logger = logging.getLogger("olive.drivers.sutter")


class Lambda10B(Device):  # FIXME create device hub
    def __init__(self, driver, port):
        super().__init__(driver)

        self._port = port
        # stream r/w pair
        self._reader, self._writer = None, None

    ##

    @property
    def is_busy(self):
        # TODO
        pass

    @property
    def is_opened(self):
        return self._reader is not None and self._writer is not None

    ##

    async def _open(self):
        loop = asyncio.get_running_loop()

        port = await self.driver.manager.request_port(self._port, self)
        self._reader, self._Writer = await open_serial_connection(
            loop=loop, url=port, baudrate=None
        )

    async def _close(self):
        self._writer.close()
        await self._writer.wait_closed()

        await self.driver.manager.release_port(self._port)

        self._reader, self._writer = None, None

    ##

    async def get_device_info(self):
        pass


class Sutter(Driver):
    def __init__(self):
        super().__init__()
        self._manager = SerialPortManager()

    ##

    @property
    def manager(self):
        return self._manager

    ##

    async def initialize(self):
        self.manager.refresh()

    def _enumerate_device_candidates(self) -> Iterable[None]:
        pass
