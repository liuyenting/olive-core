import asyncio
import logging
import math
import re
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
from typing import Iterable

from serial_asyncio import open_serial_connection

from olive.devices import AcustoOpticalModulator, wo_property, DevicePropertyDataType
from olive.devices.base import DeviceInfo
from olive.devices.error import (
    DeviceTimeoutError,
    ExceedsChannelCapacityError,
    UnsupportedClassError,
)

from ..base import Driver
from ..error import PortAlreadyAssigned
from ..utils import SerialPortManager

__all__ = ["MultiDigitalSynthesizer"]

logger = logging.getLogger("olive.drivers.aa")


@dataclass
class LineStatus:
    lineno: int
    frequency: float  # MHz
    power: float  # dBm
    switch: bool


class ControlMode(Enum):
    Internal = 0
    External = 1


class ControlVoltage(Enum):
    FIVE_VOLT = 0
    TEN_VOLT = 1


class MDSnC(AcustoOpticalModulator):
    """
    Args:
        port (str): device name
    """

    BAUDRATE = 19200

    VERSION_PATTERN = r"MDS [vV]([\w\.]+).*//"
    SERIAL_PATTERN = r"([\w]+)\s+"

    LINE_STATUS_PATTERN = r"l(\d)F(\d+\.\d+)P(\s*[+-]?\d+\.\d+)S([01])"
    POWER_RANGE_PATTERN = r"-> P[p]{4} = Power adj \([p]{4} = (\d+)->(\d+)\)"

    def __init__(self, driver, port):
        super().__init__(driver)

        self._port = port
        # stream r/w pair
        self._reader, self._writer = None, None

        # cached
        self._command_list = None
        self._n_channels = -1

    ##

    @property
    def is_busy(self):
        return False  # nothing to be busy about

    @property
    def is_opened(self):
        """Is the device opened?"""
        return self._reader is not None and self._writer is not None

    ##

    async def test_open(self):
        try:
            await super().test_open()
            await self.driver.manager.mark_port(self._port)  # mark port as in-use
            print(f"{self._port} marked")
        except (DeviceTimeoutError, PortAlreadyAssigned, SyntaxError):
            print(f"{self._port} failed")
            raise UnsupportedClassError

    async def _open(self):
        """Open connection to the synthesizer and seize its internal control."""
        loop = asyncio.get_running_loop()

        print(f"{self._port}, 1 - request and open the port")
        port = await self.driver.manager.request_port(self._port)
        self._reader, self._writer = await open_serial_connection(
            loop=loop, url=port, baudrate=self.BAUDRATE
        )

        print(f"{self._port}, 2 - get basic system info")

        self._command_list = await self._get_command_list()
        self._n_channels = await self._get_number_of_channels()

        print(f"{self._port}, 3 - reconfigure for external control")

        self.control_voltage = ControlVoltage.FIVE_VOLT
        self.control_mode = ControlMode.External

        print(f"{self._port}, 4 - sync")

        await self.sync()

        print(f"{self._port}, 5 - complete")

    async def _close(self):
        self.control_mode = ControlMode.Internal
        await self.control_mode.sync()
        await self._save_parameters()

        self._writer.close()
        await self._writer.wait_closed()

        await self.driver.manager.release_port(self._port)

        self._reader, self._writer = None, None

    ##

    async def get_device_info(self):
        # parse firmware version
        matches = re.search(
            self.VERSION_PATTERN, self._command_list, flags=re.MULTILINE
        )
        if matches:
            version = matches.group(1)
        else:
            raise SyntaxError("unable to find version string")

        # request serial
        self._writer.write(b"q\r")
        await self._writer.drain()
        serial = await self._reader.readuntil(b"?")
        serial = serial.decode()

        # parse serial
        matches = re.search(self.SERIAL_PATTERN, serial)
        if matches:
            serial = matches.group(1)
        else:
            raise SyntaxError("unable to find serial number")

        return DeviceInfo(
            version=version, vendor="AA", model="MDSnC", serial_number=serial
        )

    ##

    @wo_property(
        dtype=DevicePropertyDataType.Enum,
        enum=ControlMode,
        default=ControlMode.Internal,
    )
    async def control_mode(self, mode: ControlMode):
        """
        Adjust driver mode.

        Args:
            mode (ControlMode): control mode, either internal or external
        """
        await asyncio.sleep(0.5)  # slight delay to prevent message loss at MDS

        logger.debug(f"switching control mode to {mode.name}")
        self._writer.write(f"I{mode.value}\r".encode())
        await self._writer.drain()

    @wo_property(
        dtype=DevicePropertyDataType.Enum,
        enum=ControlVoltage,
        default=ControlVoltage.FIVE_VOLT,
    )
    async def control_voltage(self, voltage: ControlVoltage):
        """
        Adjust external driver voltage.

        Args:
            voltage (ControlVoltage): external control voltage range (5V or 10V max)
        """
        await asyncio.sleep(0.5)  # slight delay to prevent message loss at MDS

        logger.debug(f"switching control voltage to {voltage.name}")
        self._writer.write(f"V{voltage.value}\r".encode())
        await self._writer.drain()

    ##

    def get_max_channels(self):
        return self._n_channels

    def create_channel(self, new_alias):
        n_channels = self.get_max_channels()

        if len(self._channels) == n_channels:
            raise ExceedsChannelCapacityError()

        # line 1-8
        aliases = [None] * n_channels
        # re-fill
        for alias, lineno in self._channels.items():
            aliases[lineno - 1] = alias  # lines starts from 1
        # find first empty slot
        for lineno, alias in enumerate(aliases):
            if alias is None:
                lineno += 1  # lines starts from 1
                logger.debug(f'assign "{new_alias}" to line {lineno}')
                self._channels[new_alias] = lineno
                break

    ##

    async def is_enabled(self, alias):
        status = await self._get_line_status(alias)
        return status.switch

    async def enable(self, alias):
        await self._set_line_status(alias, switch=True)

    async def disable(self, alias):
        await self._set_line_status(alias, switch=False)

    ##

    async def get_frequency_range(self, alias, frange=(0, 1000)):
        state0 = await self.is_enabled(alias)
        if state0:
            await self.disable(alias)
        freq0 = await self.get_frequency(alias)

        # test lower/upper bound
        fmin = await self._set_line_status(alias, frequency=0, validate=False)
        fmax = await self._set_line_status(alias, frequency=1000, validate=False)
        fmin, fmax = fmin.frequency, fmax.frequency

        # restore original state
        await self.set_frequency(alias, freq0)
        if state0:
            await self.enable(alias)

        return (fmin, fmax)

    async def get_frequency(self, alias):
        status = await self._get_line_status(alias)
        return status.frequency

    async def set_frequency(self, alias, frequency):
        await self._set_line_status(alias, frequency=frequency)  # ensure digits

    async def get_power_range(self, alias):
        """
        Test power range for _current_ frequency setting.
        """
        state0 = await self.is_enabled(alias)
        if state0:
            await self.disable(alias)
        power0 = await self.get_power(alias)

        vmin, vmax = self._discrete_power_range()
        # test lower/upper bound by discrete power level
        pmin = await self._set_line_status(alias, discrete_power=vmin, validate=False)
        pmax = await self._set_line_status(alias, discrete_power=vmax, validate=False)
        pmin, pmax = pmin.power, pmax.power

        # restore original state
        await self.set_power(alias, power0)
        if state0:
            await self.enable(alias)

        return (pmin, pmax)

    async def get_power(self, alias):
        status = await self._get_line_status(alias)
        return status.power

    async def set_power(self, alias, power):
        await self._set_line_status(alias, power=power)

    ##

    async def _get_command_list(self, timeout=1, n_retry=3):
        """
        Get command list using dummy <ENTER>.

        Args:
            timeout (int, optional): timeout in seconds

        Returns:
            (str): decoded raw command list
        """
        if self._command_list is not None:
            return self._command_list
        logger.debug(f"command list not cached")

        for i_retry in range(n_retry):
            self._writer.write(b"\r")
            await self._writer.drain()

            try:
                # wait 3 seconds to load, normally, this is enough
                command_list = await asyncio.wait_for(
                    self._reader.readuntil(b"?"), timeout=timeout
                )
                return command_list.decode()
            except asyncio.TimeoutError:
                logger.debug(f"command list request timeout, trial {i_retry+1}")
        else:
            raise DeviceTimeoutError()

    @lru_cache(maxsize=1)
    def _discrete_power_range(self):
        """
        Use fast channel command description to boostrap discrete steps.
        """
        matches = re.search(
            self.POWER_RANGE_PATTERN, self._command_list, flags=re.MULTILINE
        )
        if matches:
            return (int(matches.group(1)), int(matches.group(2)))
        else:
            raise SyntaxError("unable to parse discrete power range")

    async def _get_line_status(self, alias, from_response=False) -> LineStatus:
        if not from_response:
            self._writer.write(f"L{self._channels[alias]}\r".encode())
            await self._writer.drain()

        response = await self._reader.readuntil(b"\r")
        response = response.decode()

        status = self._parse_line_status_response(response)
        return status

    @classmethod
    def _parse_line_status_response(self, response) -> LineStatus:
        """
        Parse line status using command response.

        Args:
            response (str): response string

        Returns:
            (LineStatus): parsed LineStatus object
        """
        matches = re.search(self.LINE_STATUS_PATTERN, response)
        if matches:
            return LineStatus(
                lineno=int(matches.group(1)),
                frequency=float(matches.group(2)),
                power=float(matches.group(3)),
                switch=(matches.group(4) == "1"),
            )
        else:
            raise SyntaxError("unable to parse line status")

    async def _set_line_status(self, alias, validate=True, **kwargs) -> LineStatus:
        # build command string
        commands = [f"L{self._channels[alias]}"]
        for key, value in kwargs.items():
            if key == "frequency":
                command = f"F{value:3.2f}"
            elif key == "power":
                command = f"D{value:2.2f}"
            elif key == "discrete_power":
                command = f"P{value}"
            elif key == "switch":
                command = f"O{int(value)}"
            commands.append(command)
        commands = "".join(commands) + "\r"
        logger.debug(f"write [{commands[:-1]}]")

        # send it
        self._writer.write(commands.encode())
        await self._writer.drain()

        # clear out receive buffer
        status = await self._get_line_status(alias, from_response=True)
        if validate:
            for key, value0 in kwargs.items():
                if key not in ("frequency", "power", "switch"):
                    continue
                value = getattr(status, key)
                if (isinstance(value, float) and not math.isclose(value, value0)) or (
                    value != value0
                ):
                    raise ValueError(
                        f"{key} (target: {value0}, current: {value}) out of range"
                    )

        return status

    async def _get_number_of_channels(self):
        """Get number of channels using general status dump."""
        # simple dump
        self._writer.write(b"S")
        await self._writer.drain()

        # wait response
        status = await self._reader.readuntil(b"?")
        status = status.decode()

        return len(re.findall(r"l\d F", status))

    async def _save_parameters(self):
        """Save parameters in the EEPROM."""
        self._writer.write(b"E\r")
        await self._writer.drain()


class MultiDigitalSynthesizer(Driver):
    def __init__(self):
        super().__init__()
        self._manager = SerialPortManager()

    ##

    @property
    def manager(self):
        return self._manager

    ##

    async def initialize(self):
        self.manager.refresh()

    def _enumerate_device_candidates(self) -> Iterable[MDSnC]:
        candidates = [MDSnC(self, port) for port in self.manager.list_ports()]
        return candidates
