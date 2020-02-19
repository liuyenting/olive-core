import asyncio
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from functools import lru_cache
import logging
import re
from typing import Iterable

from serial import Serial, SerialException
from serial.tools import list_ports
from serial_asyncio import open_serial_connection

from olive.drivers.base import Driver
from olive.devices import AcustoOpticalModulator
from olive.devices.base import DeviceInfo
from olive.devices.error import UnsupportedClassError, DeviceTimeoutError
from olive.drivers.utils import SerialPortManager
from olive.devices.error import ExceedsChannelCapacityError

__all__ = ["MultiDigitalSynthesizer"]

logger = logging.getLogger(__name__)


@dataclass
class LineStatus:
    line: int = 0  # line number
    frequency: float = 0  # MHz
    power: float = 0  # dB
    switch: bool = False
    is_dirty: bool = False


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

    BAUDRATE = 19200

    VERSION_PATTERN = r"MDS [vV]([\w\.]+).*//"
    SERIAL_PATTERN = r"([\w]+)\s+"

    LINE_STATUS_PATTERN = r"l\dF(\d+\.\d+)P(\s*[+-]?\d+\.\d+)S([01])"
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
            await self.open()
            logger.info(f".. {self.info}")
            # TODO verify device version
        except (DeviceTimeoutError, SyntaxError):
            raise UnsupportedClassError
        finally:
            await self.close()

    async def _open(self):
        """Open connection to the synthesizer and seize its internal control."""
        loop = asyncio.get_running_loop()

        port = await self.driver.manager.request_port(self._port)
        self._reader, self._writer = await open_serial_connection(
            loop=loop, url=port, baudrate=self.BAUDRATE
        )

        self._command_list = await self._get_command_list()
        self._n_channels = await self._get_number_of_channels()

        await self._set_control_voltage(ControlVoltage.FIVE_VOLT)
        await self._set_control_mode(ControlMode.EXTERNAL)

    async def _get_device_info(self):
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

    async def _close(self):
        await self._set_control_mode(ControlMode.INTERNAL)
        await self._save_parameters()

        self._writer.close()
        await self._writer.wait_closed()

        self.driver.manager.release_port(self._port)

        self._reader, self._writer = None, None

    ##

    def enumerate_properties(self):
        return ("control_mode", "control_voltage", "discrete_power_range")

    ##

    def number_of_channels(self):
        return self._n_channels

    def new_channel(self, new_alias):
        if len(self.defined_channels()) == self.number_of_channels():
            raise ExceedsChannelCapacityError()

        # line 1-8
        aliases = [None] * self.number_of_channels()
        # re-fill
        # NOTE lines [1, 8], but index [0, 7]
        for alias, status in self._channels.items():
            aliases[status.line - 1] = alias
        # find first empty slot
        for line, alias in enumerate(aliases):
            if alias is None:
                logger.debug(f'assign "{new_alias}" to line {line}')
                self._channels[new_alias] = LineStatus(line=line + 1, is_dirty=True)
                break

    ##

    def write(self, alias, **kwargs):
        # build command string
        commands = [f"L{self._channels[alias].line}"]
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
        logger.debug(f"write [{commands}]")

        # send it
        self._writer.write(commands.encode())

        # wait
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._writer.drain())

        # mark as dirty
        self._channels[alias].is_dirty = True

    def read(self, terminator=b"\r"):
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(self._reader.readuntil(terminator))
        return response.decode()

    def is_enabled(self, alias):
        return self._get_line_status(alias).switch

    def _get_line_status(self, alias, trigger=False):
        if self._channels[alias].is_dirty:
            logger.debug(f'"{alias}" requires status update')
            self._refresh_line_status(alias, trigger)
        return self._channels[alias]

    def _refresh_line_status(self, alias, trigger=True):
        """
        Get line status.

        Args:
            alias (str): channel alias
            trigger (bool, optional): trigger the controller to respond
        """
        if trigger:
            self.write(alias)
        new_status = self.read()

        # parse line
        matches = re.search(self.LINE_STATUS_PATTERN, new_status)
        if matches:
            status = self._channels[alias]
            status.frequency = float(matches.group(1))
            status.power = float(matches.group(2))
            status.switch = matches.group(3) == "1"
        else:
            raise SyntaxError("unable to parse line status")

    def enable(self, alias):
        self._set_switch(alias, True)

    def disable(self, alias):
        self._set_switch(alias, False)

    def _set_switch(self, alias, on: bool):
        self.write(alias, switch=on)

        # verify
        status = self._get_line_status(alias, trigger=False)
        if status.switch ^ on:
            state = "enable" if on else "disable"
            raise RuntimeError(f'unable to {state} "{alias}"')

    ##

    def get_frequency_range(self, alias, frange=(0, 1000)):
        state0 = self.is_enabled(alias)
        self.disable(alias)
        freq0 = self.get_frequency(alias)

        # test lower bound
        self.set_frequency(alias, 0)
        fmin = self.get_frequency(alias)
        # test upper bound
        self.set_frequency(alias, 1000)
        fmax = self.get_frequency(alias)

        # restore original state
        self.set_frequency(alias, freq0)
        if state0:
            self.enable(alias)

        return (fmin, fmax)

    def get_frequency(self, alias):
        return self._get_line_status(alias).frequency

    def set_frequency(self, alias, frequency):
        self.write(alias, frequency=frequency)

        # verify
        status = self._get_line_status(alias, trigger=False)
        if status.frequency != frequency:
            logger.warning(f"frequency out-of-range ({frequency} MHz), ignored")

    def get_power_range(self, alias):
        """
        Test power range for _current_ frequency setting.
        """
        state0 = self.is_enabled(alias)
        self.disable(alias)
        power0 = self.get_power(alias)

        loop = asyncio.get_event_loop()

        vmin, vmax = self._discrete_power_range()
        # test lower/upper bound by discrete power level
        self._writer.write(f"L{alias}P{vmin}\r".encode())
        loop.run_until_complete(self._writer.drain())
        pmin = self.get_power(alias)
        self._writer.write(f"L{alias}P{vmax}\r".encode())
        loop.run_until_complete(self._writer.drain())
        pmax = self.get_power(alias)

        # restore original state
        self.set_power(alias, power0)
        if state0:
            self.enable(alias)

        return (pmin, pmax)

    def get_power(self, alias):
        loop = asyncio.get_event_loop()
        status = loop.run_until_complete(self._get_line_status(alias))
        return status.power

    def set_power(self, alias, power):
        loop = asyncio.get_event_loop()

        self._writer.write(f"L{self._channels[alias]}D{power:2.2f}\r".encode())
        loop.run_until_complete(self._writer.drain())

        # verify
        status = loop.run_until_complete(self._get_line_status(alias, trigger=False))
        if status.power != power:
            logger.warning(f"power out-of-range ({power} dBm), ignored")

    ##

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

    async def _set_control_mode(self, mode: ControlMode):
        """
        Adjust driver mode.

        Args:
            mode (ControlMode): control mode, either internal or external
        """
        await asyncio.sleep(0.5)  # slight delay to prevent message loss at MDS

        logger.debug(f"switching control mode to {mode.name}")
        self._writer.write(f"I{mode.value}\r".encode())
        await self._writer.drain()

    async def _set_control_voltage(self, voltage: ControlVoltage):
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
                break
            except asyncio.TimeoutError:
                logger.debug(f"command list request timeout, trial {i_retry+1}")
        else:
            raise DeviceTimeoutError()

    ##

    async def _save_parameters(self):
        """Save parameters in the EEPROM."""
        self._writer.write(b"E\r")
        await self._writer.drain()

    async def _get_number_of_channels(self):
        """Get number of channels using general status dump."""
        # simple dump
        self._writer.write(b"S")
        await self._writer.drain()

        # wait response
        status = await self._reader.readuntil(b"?")
        status = status.decode()

        return len(re.findall(r"l\d F", status))


class MultiDigitalSynthesizer(Driver):
    def __init__(self):
        super().__init__()
        self._manager = SerialPortManager()

    ##

    @property
    def manager(self):
        return self._manager

    ##

    def initialize(self):
        self.manager.refresh()

    def _enumerate_device_candidates(self) -> Iterable[MDSnC]:
        candidates = [MDSnC(self, port) for port in self.manager.list_ports()]
        return candidates

