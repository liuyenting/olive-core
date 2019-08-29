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
    UnableToParseDiscretePowerRangeError,
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

        self._discrete_power_range = None

    ##

    @retry(UnableToParseVersionError, logger=logger)
    def open(self):
        """Open connection to the synthesizer and seize its internal control."""
        self.handle.open()

        try:
            # use version string to probe validity
            response = self._get_command_list()
            self._parse_version(response)
        except UnableToParseVersionError:
            raise UnsupportedDeviceError

        # save discrete power range in single run
        self._discrete_power_range = self._parse_discrete_power_range(response)

        self._set_control_voltage(ControlVoltage.FIVE_VOLT)
        self._set_control_mode(ControlMode.EXTERNAL)

        super().open()

    def close(self):
        self._save_parameters()
        self._set_control_mode(ControlMode.INTERNAL)

        self.handle.flush()
        self.handle.close()

        super().close()

    ##

    def enumerate_properties(self):
        return ("version", "freq_range")

    ##

    def is_enabled(self, channel):
        self.handle.write(f"L{channel}\r".encode())
        status = self._get_line_status(channel)
        return status.switch

    def enable(self, channel, force=True):
        self.set_switch(channel, True, force)

    def disable(self, channel, force=True):
        self.set_switch(channel, False, force)

    def set_switch(self, channel, on: bool, force=True):
        on = 1 if on else 0
        self.handle.write(f"L{channel}O{on}\r".encode())
        # verify
        data = self.handle.read_until("\r").decode("utf-8")
        status = self._parse_line_status(data)
        if status.switch ^ on:
            text = "enable" if on else "disable"
            msg = f"unable to {text} channel {channel}"
            if force:
                raise IOError(msg)
            else:
                logger.warning(msg)

    def get_frequency(self, channel):
        status = self._get_line_status(channel)
        return status.frequency

    def set_frequency(self, channel, frequency, force=False):
        self.handle.write(f"L{channel}F{frequency:3.2f}\r".encode())
        # verify
        data = self.handle.read_until("\r").decode("utf-8")
        status = self._parse_line_status(data)
        if status.frequency != frequency:
            msg = f"frequency value out-of-range ({frequency} MHz)"
            if force:
                raise ValueError(msg)
            else:
                logger.warning(msg)

    def get_power(self, channel):
        status = self._get_line_status(channel)
        return status.power

    def set_power(self, channel, power, force=False):
        self.handle.write(f"L{channel}D{power:2.2f}\r".encode())
        # verify
        data = self.handle.read_until("\r").decode("utf-8")
        status = self._parse_line_status(data)
        if status.power != power:
            msg = f"power value out-of-range ({power} dBm)"
            if force:
                raise ValueError(msg)
            else:
                logger.warning(msg)

    @property
    def handle(self):
        return self._handle

    """
    Property accessors.
    """

    def _get_command_list(self):
        # trigger message dump
        self.handle.write(b"\r")
        # capture the prompt
        return self.handle.read_until("?").decode("utf-8")

    def _parse_version(self, response, pattern=r"MDS [vV]([\w\.]+).*//"):
        # scan for version string
        matches = re.search(pattern, response, flags=re.MULTILINE)
        if matches:
            return matches.group(1)
        else:
            raise UnableToParseVersionError

    def _parse_discrete_power_range(
        self, response, pattern=r"-> P[p]{4} = Power adj \([p]{4} = (\d+)->(\d+)\)"
    ):
        """
        Use fast channel command description to determine range, instead of verify
        values one-by-one.
        """
        matches = re.search(pattern, response, flags=re.MULTILINE)
        if matches:
            return (int(matches.group(1)), int(matches.group(2)))
        else:
            raise UnableToParseDiscretePowerRangeError

    def _get_freq_range(self, test_on=1):
        """
        Args:
            test_on (int, optional): test frequency setting on this line
        """
        state_ori = self.is_enabled(test_on)
        self.disable(test_on)
        freq_ori = self.get_frequency(test_on)

        # test lower bound
        self.set_frequency(test_on, 0)
        freq_min = self.get_frequency(test_on)
        # test upper bound
        self.set_frequency(test_on, 1000)
        freq_max = self.get_frequency(test_on)

        # restore original state
        self.set_frequency(test_on, freq_ori)
        if state_ori:
            self.enable(test_on)

        return (freq_min, freq_max)

    def _get_power_range(self, test_on):
        """
        Test power range for _current_ frequency setting.

        Args:
            test_on (int): test power range on this line
        """
        state_ori = self.is_enabled(test_on)
        self.disable(test_on)
        power_ori = self.get_power(test_on)

        dmin, dmax = self._discrete_power_range
        # test lower bound
        self.handle.write(f"L{test_on}P{dmin}\r".encode())
        power_min = self.get_power(test_on)
        # test upper bound
        self.handle.write(f"L{test_on}P{dmax}\r".encode())
        power_max = self.get_power(test_on)

        # restore original state
        self.set_power(test_on, power_ori)
        if state_ori:
            self.enable(test_on)

        return (power_min, power_max)

    """
    Private helper functions and constants.
    """

    def _get_line_status(self, channel):
        self.handle.reset_input_buffer()
        self.handle.write(f"L{channel}\r".encode())
        data = self.handle.read_until("\r").decode("utf-8")
        return self._parse_line_status(data)

    def _parse_line_status(
        self, data, pattern=r"l(\d)F(\d+\.\d+)P(\s*[+-]?\d+\.\d+)S([01])"
    ):
        matches = re.search(pattern, data)
        if matches:
            return LineStatus(
                channel=int(matches.group(1)),
                frequency=float(matches.group(2)),
                power=float(matches.group(3)),
                switch=(matches.group(4) == "1"),
            )
        else:
            # use repr() to show invisible characters
            raise UnableToParseLineStatusError(f"trying to parse {repr(data)}")

    def _set_control_mode(self, mode: ControlMode):
        """Adjust driver mode."""
        logger.debug(f"switching control mode to {mode.name}")
        self.handle.write(f"I{mode.value}\r".encode())

    def _set_control_voltage(self, voltage: ControlVoltage):
        """
        Adjust external driver voltage.

        Note:
            Due to unknown reason, fast control 'V0\r' will cause the controller to
            return complete help message. Fallback to slower interactive mode, 'v\r0\r'.
        """
        logger.debug(f"switching control voltage to {voltage.name}")
        # self.handle.write(f"V{voltage.value}\r".encode())
        self.handle.write(b"v\r")
        self.handle.read_until(">")
        self.handle.write(f"{voltage.value}\r".encode())
        self.handle.read_until("?")

    def _save_parameters(self):
        """Save parameters in the EEPROM."""
        self.handle.write(b"E\r")

    def _dump_status(self):
        """Dump status string from all lines."""
        self.handle.write(b"S")
        response = self.handle.read_until("?").decode()
        print(response)


class MultiDigitalSynthesizer(Driver):
    def __init__(self):
        super().__init__()

    ##

    def initialize(self):
        super().initialize()

    def shutdown(self):
        super().shutdown()

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
        return tuple()

    def get_attribute(self, name):
        raise NotImplementedError("nothing to get")

    def set_attribute(self, name, value):
        raise NotImplementedError("nothing to set")

