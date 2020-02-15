import asyncio
from collections import namedtuple
from enum import Enum
import logging
import re

from serial import Serial, SerialException
from serial.tools import list_ports

from olive.drivers.base import Driver
from olive.devices import AcustoOpticalModulator
from olive.devices.base import DeviceInfo
from olive.devices.errors import UnsupportedDeviceError

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

    async def test_open(self):
        logger.debug(f"testing {self.handle.port}")
        try:
            self.handle.open()
            print('opened')
            logger.info(f".. {self.info}")
        except (SyntaxError, SerialException):
            raise UnsupportedDeviceError
        finally:
            self.handle.close()
            print('closed')

    async def _open(self):
        """Open connection to the synthesizer and seize its internal control."""
        self.handle.open()

        self._discrete_power_range = self._get_discrete_power_range()

        self._set_control_voltage(ControlVoltage.FIVE_VOLT)
        self._set_control_mode(ControlMode.EXTERNAL)

    async def _close(self):
        self._save_parameters()
        self._set_control_mode(ControlMode.INTERNAL)

        self.handle.close()

    ##

    def enumerate_properties(self):
        return ("control_mode", "control_voltage", "discrete_power_range")

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

    def get_frequency_range(self, channel):
        state_ori = self.is_enabled(channel)
        self.disable(channel)
        freq_ori = self.get_frequency(channel)

        # test lower bound
        self.set_frequency(channel, 0)
        freq_min = self.get_frequency(channel)
        # test upper bound
        self.set_frequency(channel, 1000)
        freq_max = self.get_frequency(channel)

        # restore original state
        self.set_frequency(channel, freq_ori)
        if state_ori:
            self.enable(channel)

        return (freq_min, freq_max)

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

    def get_power_range(self, channel):
        """
        Test power range for _current_ frequency setting.
        """
        state_ori = self.is_enabled(channel)
        self.disable(channel)
        power_ori = self.get_power(channel)

        dmin, dmax = self._discrete_power_range
        # test lower bound
        self.handle.write(f"L{channel}P{dmin}\r".encode())
        power_min = self.get_power(channel)
        # test upper bound
        self.handle.write(f"L{channel}P{dmax}\r".encode())
        power_max = self.get_power(channel)

        # restore original state
        self.set_power(channel, power_ori)
        if state_ori:
            self.enable(channel)

        return (power_min, power_max)

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

    ##

    @property
    def busy(self):
        return False

    @property
    def handle(self):
        return self._handle

    @property
    def info(self) -> DeviceInfo:
        # trigger command list dump
        self.handle.write(b"\r")
        # firmware version
        try:
            response = self.handle.read_until("?").decode("utf-8")
            print(response)
            version = self._parse_version(response)
            print(version)
        except (ValueError, UnicodeDecodeError):
            raise SyntaxError("unable to parse version")

        # serial number
        self.handle.write(b"q\r")
        response = self.handle.read_until("?").decode("utf-8")
        print(response)
        matches = re.search(r"([\w]+)\s+", response)
        if matches:
            sn = matches.group(1)
        else:
            raise SyntaxError("unable to parse serial number")

        return DeviceInfo(version=version, vendor="AA", model="MDSnC", serial_number=sn)

    """
    Property accessors.
    """

    def _get_discrete_power_range(
        self, pattern=r"-> P[p]{4} = Power adj \([p]{4} = (\d+)->(\d+)\)"
    ):
        """
        Use fast channel command description to determine range, instead of verify
        values one-by-one.
        """
        # trigger command list dump
        self.handle.write(b"\r")
        response = self.handle.read_until("?").decode("utf-8")
        matches = re.search(pattern, response, flags=re.MULTILINE)
        if matches:
            return (int(matches.group(1)), int(matches.group(2)))
        else:
            raise SyntaxError("unable to parse discrete power range")

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

    """
    Private helper functions and constants.
    """

    def _parse_version(self, response, pattern=r"MDS [vV]([\w\.]+).*//"):
        # scan for version string
        matches = re.search(pattern, response, flags=re.MULTILINE)
        if matches:
            return matches.group(1)
        else:
            raise SyntaxError("unable to parse version string")

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
            raise SyntaxError("unable to parse line status")

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

    def enumerate_devices(self) -> MDSnC:
        loop = asyncio.get_event_loop()

        devices = [MDSnC(self, info.device) for info in list_ports.comports()]
        results = loop.run_until_complete(
            asyncio.gather(*[d.test_open() for d in devices], return_exceptions=True)
        )

        valid_devices = []
        for device, result in zip(devices, results):
            if result is None:
                valid_devices.append(device)
            else:
                try:
                    raise result
                except UnsupportedDeviceError:
                    continue
        return tuple(valid_devices)

