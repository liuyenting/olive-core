from abc import ABCMeta, abstractmethod
import logging

import serial
from serial.tools import list_ports

from olive.devices.base import Device

__all__ = ["SerialDevice"]

logger = logging.getLogger(__name__)


class SerialDevice(Device, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self._handle = serial.Serial()

    def discover(cls):
        """List all the serial ports."""
        return [info.device for info in list_ports.comports()]

    def initialize(
        self, port, baudrate=9600, read_timeout=None, write_timeout=None, **kwargs
    ):
        """
        Open port.

        Args:
            port (str): device name
            baudrate (int): baud rate
            read_timeout (float): read timeout in seconds
                Possible values for timeout includes
                - None, wait untile requested condition is satisfied
                - 0, non-blocking mode, return immediately with 0 up to requested
                    number of bytes.
                - x, set timeout to x seconds.
            write_timeout (float):write timeout in seconds
                Same as read_timeout.
            **kwargs: Other pySerial supported settings.
                write_timeout, inter_byte_timeout, dsrdtr, baudrate, timeout, parity, 
                bytesize, rtscts, stopbits, xonxoff
        Note:
            The timeout argument will configure both read and write timeout.
        """
        self.handle.port = port
        kwargs = {
            **kwargs,
            **{
                "baudrate": baudrate,
                "timeout": read_timeout,
                "write_timeout": write_timeout,
            },
        }
        self.handle.apply_settings(kwargs)

        self.handle.open()
        logger.debug(f"established connection with {port}")

    def close(self):
        self.handle.close()

    @property
    def handle(self):
        return self._handle
