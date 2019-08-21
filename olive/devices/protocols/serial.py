from abc import ABCMeta

from serial.tools import list_ports

from olive.devices.base import Device


class SerialDevice(Device, metaclass=ABCMeta):
    def discover(cls):
        """List all the serial ports."""
        return list_ports.comports()

    def initialize(self):
        pass

    def close(self):
        pass
