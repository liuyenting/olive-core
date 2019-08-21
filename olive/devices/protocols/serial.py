from abc import ABCMeta

import serial

from olive.devices.base import Device


class SerialDevice(Device, metaclass=ABCMeta):
    def discover(cls):
        """List all the serial ports."""
        return serial.tools.list_ports()

    def initialize(self):
        pass

    def close(self):
        pass
