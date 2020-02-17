import logging

from serial.tools import list_ports

from olive.devices.base import Device
from olive.drivers.base import Driver

__all__ = ["SerialDriver"]

logger = logging.getLogger(__name__)


class SerialDevice(Device):
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

    async def enumerate_devices(self):
        ports = [port.device for port in list_ports.comports()]
        logger.debug(f"found {len(ports)} COM port(s)")

        # TODO wrap them in SerialDevice
