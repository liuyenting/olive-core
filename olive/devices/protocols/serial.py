from abc import ABCMeta

import serial
from serial.tools import list_ports

from olive.devices.base import Device


class SerialDevice(Device, metaclass=ABCMeta):
    def __init__(self):
        super().__init__()
        self._handle = serial.Serial()

    def discover(cls):
        """List all the serial ports."""
        return list_ports.comports()

    def initialize(self, port, timeout=500, **kwargs):
        """
        Open port.

        Args:
            port (str): device name
            timeout (int): timeout in ms
        """
        self.handle.port = port
        self.handle.timeout = timeout / 1000

        # TODO update handle using kwargs

        self.handle.open()

    def close(self):
        self.handle.close()

    @property
    def handle(self):
        return self._handle
