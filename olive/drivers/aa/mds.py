import asyncio
from collections import namedtuple
from enum import Enum
import logging
import re
from typing import Union

from serial import Serial
from serial.tools import list_ports

from olive.core import Driver
from olive.core.utils import retry
from olive.devices import AcustoOpticalModulator
from olive.devices.errors import UnsupportedDeviceError

from olive.drivers.aa.errors import (
    UnableToParseLineStatusError,
    UnableToParseVersionError,
)

__all__ = ["MultiDigitalSynthesizer"]

logger = logging.getLogger(__name__)


LineStatus = namedtuple("LineStatus", ["channel", "frequency", "power", "switch"])


class ControlMode(Enum):
    INTERNAL = 0
    EXTERNAL = 1


class ControlVoltage(Enum):
    FIVE_VOLT = 0
    TEN_VOLT = 1


class MDSnC(AcustoOpticalModulator):
    """
    Args:
        port (str): device name
        timeout (int): timeout in ms
    """

    def __init__(self, driver, port, timeout=1000):
        super().__init__(driver)

        if timeout:
            timeout /= 1000

        ser = Serial()
        ser.port = port
        ser.baudrate = 19200
        ser.timeout = timeout
        ser.write_timeout = timeout
        self._handle = ser

    ##

    def open(self):
        """
        Open connection with the synthesizer.
        """
        self.handle.open()

        # use version string to probe validity
        try:
            self._get_version()
        except UnableToParseVersionError:
            raise UnsupportedDeviceError

        #self._set_control_voltage(ControlVoltage.FIVE_VOLT)
        self._set_control_mode(ControlMode.EXTERNAL)

        super().open()

    def close(self):
        #self._save_parameters()
        self._set_control_mode(ControlMode.INTERNAL)
        self.handle.close()

        super().close()

    ##

    def enumerate_properties(self):
        return ("version",)

    def get_property(self, name):
        func = getattr(self, f"_get_{name}")
        return func()

    def set_property(self, name, value):
        pass

    ##

    def get_frequency(self, channel):
        status = self._get_line_status(channel)
        return status.frequency

    def set_frequency(self, channel, frequency):
        self.handle.write(f"L{channel}F{frequency:3.3f}\r".encode())

    def get_power(self, channel):
        status = self._get_line_status(channel)
        return status.power

    def set_power(self, channel, power):
        pass

    @property
    def handle(self):
        return self._handle

    """
    Property accessors.
    """

    @retry(UnableToParseVersionError, logger=logger)
    def _get_version(self, pattern=r"MDS [vV]([\w\.]+).*//"):
        # trigger message dump
        self.handle.write(b"\r")
        # capture the help message
        data = self.handle.read_until("?").decode("utf-8")
        # scan for version string
        matches = re.search(pattern, data, flags=re.MULTILINE)
        if matches:
            return matches.group(1)
        else:
            raise UnableToParseVersionError

    """
    Private helper functions and constants.
    """

    def _get_line_status(self, channel):
        self.handle.reset_input_buffer()
        self.handle.write(f"L{channel}\r".encode())
        data = self.handle.read_until('\r').decode("utf-8")
        return self._parse_line_status(data)

    def _parse_line_status(self, data, pattern=r"l(\d)F(\d+\.\d+)P(\d+\.\d+)S([01])"):
        matches = re.search(pattern, data)
        if matches:
            return LineStatus(
                channel=int(matches.group(1)),
                frequency=float(matches.group(2)),
                power=float(matches.group(3)),
                switch=bool(matches.group(4)),
            )
        else:
            raise UnableToParseLineStatusError(f'"{data}"')

    def _set_control_mode(self, mode: ControlMode):
        """Adjust driver mode."""
        logger.info(f"switching control mode to {mode.name}")
        self.handle.write(f"I{mode.value}\r".encode())

    def _set_control_voltage(self, voltage: ControlVoltage):
        """Adjust external driver voltage."""
        logger.info(f"switching control voltage to {voltage.name}")
        self.handle.write(f"V{voltage.value}\r".encode())

    def _save_parameters(self):
        """Save parameters in the EEPROM."""
        self.handle.write(b"E\r")


class MultiDigitalSynthesizer(Driver):
    def __init__(self):
        super().__init__()

    ##

    def initialize(self):
        super().initialize()

    def shutdown(self):
        super().initialize()

    def enumerate_devices(self) -> Union[MDSnC]:
        loop = asyncio.get_event_loop()

        async def test_device(device):
            """Test each port using their own thread."""

            def _test_device(device):
                logger.info(f"testing {device.handle.name}...")
                device.open()
                device.close()

            return await loop.run_in_executor(device.executor, _test_device, device)

        devices = [MDSnC(self, info.device) for info in list_ports.comports()]
        testers = asyncio.gather(
            *[test_device(device) for device in devices], return_exceptions=True
        )
        results = loop.run_until_complete(testers)

        valid_devices = []
        for port, result in zip(devices, results):
            if isinstance(result, UnsupportedDeviceError):
                continue
            elif result is None:
                valid_devices.append(port)
            else:
                # unknown exception occurred
                raise result
        return tuple(valid_devices)

    ##

    def enumerate_attributes(self):
        pass

    def get_attribute(self, name):
        pass

    def set_attribute(self, name, value):
        pass

