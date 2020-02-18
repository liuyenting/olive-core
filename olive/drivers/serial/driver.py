import asyncio
import logging

from serial.tools import list_ports
from serial_asyncio import open_serial_connection

from olive.devices.base import Device, DeviceInfo
from olive.drivers.base import Driver

__all__ = ["SerialDriver"]

logger = logging.getLogger(__name__)


class SerialDeviceBase(Device):
    def __init__(self, driver, port, **kwargs):
        super().__init__(driver, parent=kwargs.pop("parent", None))

        self._reader, self._writer = None, None

    def __eq__(self, other):
        pass

    ##

    @property
    def info(self) -> DeviceInfo:
        pass

    @property
    def is_busy(self):
        pass

    @property
    def is_opened(self):
        pass

    ##

    async def test_open(self):
        pass

    async def _open(self):
        pass

    async def _close(self):
        pass

    ##

    async def enumerate_properties(self):
        # TODO return checksum state
        pass


class SerialDriver(Driver):
    """
    A template driver class for other drivers to build upon.

    This class does _not_ have initialize/shutdown method implements to ensure it can never be instantiate.

    When a SerialDevice is occupied, SerialDriver automatically locks it using Conditions to prevent race condition due to async access.
    """

    def register(self, device: Device):
        super().register(device)
        # TODO lock device

    def unregister(self, device: Device):
        super().register(device)
        # TODO unlock device

    ##

    async def _enumerate_devices(self):
        ports = [port.device for port in list_ports.comports()]
        logger.debug(f"found {len(ports)} COM port(s)")

        return [SerialDeviceBase(port) for port in ports]
