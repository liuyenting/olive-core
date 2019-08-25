from abc import ABCMeta, abstractmethod
import logging

import serial
from serial.tools import list_ports

from olive.devices.protocols.base import Protocol

__all__ = ["SerialDevice"]

logger = logging.getLogger(__name__)


class Serial(Protocol, metaclass=ABCMeta):
    @abstractmethod
    def __init__(self):
        super().__init__()
        self._handle = serial.Serial()

    @classmethod
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
        logger.debug(f"established connection to {port}")

        super().initialize()

    def close(self):
        self.handle.close()
        logger.debug(f"connection to {self.handle.port} closed")

        super().close()

    def get_attribute(self, name):
        return getattr(self.handle, name)

    def set_attribute(self, name, value):
        setattr(self.handle, name, value)

    def bytes_waiting(self):
        """
        Return number of bytes in the buffer.

        Returns:
            (tuple): tuple containing
                in_waiting (int): number of bytes in the input buffer
                out_waiting (int): number of bytes in the output buffer
        """
        return (self.handle.in_waiting, self.handle.out_waiting)

    def flush(self):
        """Flush the I/O buffer."""
        self.handle.flush()

    def read(self, nbytes=None, pattern=None):
        """Read specified number of bytes from the device."""
        pass

    def write(self, buffer):
        """Write the data to the device."""
        pass

    @property
    def handle(self):
        return self._handle
