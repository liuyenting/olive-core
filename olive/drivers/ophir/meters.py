from abc import abstractmethod
import logging
import struct
from typing import Union
import zlib

from serial import Serial
from serial.tools import list_ports

from olive.core import Driver
from olive.devices import SensorAdapter

from olive.drivers.ophir.sensors import Photodiode

__all__ = ["Ophir", "Nova2"]

logger = logging.getLogger(__name__)


class OphirPowerMeter(SensorAdapter):
    """
    Base class for Ophir power meters.

    Args:
        port (str): device name
        baudrate (int): baud rate
        timeout (int): timeout in ms
    """

    def __init__(self, driver, port, baudrate, timeout=1000):
        super().__init__(driver)

        if timeout:
            timeout /= 1000

        ser = Serial()
        ser.port = port
        ser.baudrate = baudrate
        ser.timeout = timeout
        ser.write_timeout = timeout
        self._handle = ser

    ##

    def enumerate_properties(self):
        return ("head_type",)

    ##

    @property
    def handle(self):
        return self._handle

    """
    Property accessors.
    """

    def _get_head_type(self):
        self.handle.write(b"$HT\r")
        response = self.handle.read_until("\r").decode("utf-8")
        # LaserStar and Nova-II append the measurement, split them by space
        response = response.strip("* ").split(" ")[0]
        try:
            return {"SI": Photodiode, "XX": None}[response]
        except KeyError:
            raise RuntimeError(f'unknown head type "{response}"')

    """
    Private helper functions and constants.
    """

    def _set_full_duplex(self):
        logger.debug("setting FULL duplex mode")
        self.handle.write(b"$DU\r")
        response = self.handle.read_until("\r").decode("utf-8")
        if "FULL DUPLEX" in response:
            return
        elif "RS232 SPECIFIC" in response:
            # V-USB, ignored
            return

    def _save_configuration(self):
        self.handle.write(b"$IC")


class Nova2(OphirPowerMeter):
    """
    Handheld Laser Power & Energy Meter. P/N 7Z01550.

    Compatible with all standard Ophir Thermopile, BeamTrack, Pyroelectric and Photodiode sensors.
    """

    def open(self):
        self.handle.open()
        self._set_full_duplex()

        super().open()

    def close(self):
        self._save_configuration()
        super().close()

    ##

    def enumerate_properties(self):
        return tuple() + super().enumerate_properties()

    ##

    # TODO power meter related operations

    ##

    """
    Property accessors.
    """

    """
    Private helper functions and constants.
    """

    def _get_lcd_scanlines(self):
        """Returns an 80-character, 40-byte hex string."""
        for row in range(0, 240):
            self.handle.write(f"$DI{row}\r".encode())
            data = self.handle.read_until("\r")
            if data[0] == b"*":
                yield bytearray.fromhex(data[1:])
            else:
                raise RuntimeError(
                    f"unknown error occurred during scanline ({row}) readout"
                )


class Ophir(Driver):
    def __init__(self):
        super().__init__()

    ##

    def initialize(self):
        super().initialize()

    def shutdown(self):
        super().shutdown()

    def enumerate_devices(self) -> Union[Photodiode]:
        pass

    ##

    def enumerate_attributes(self):
        return tuple()

    def get_attribute(self, name):
        raise NotImplementedError("nothing to get")

    def set_attribute(self, name, value):
        raise NotImplementedError("nothing to set")
