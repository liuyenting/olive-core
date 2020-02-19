import asyncio
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from functools import partial
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
    frequency: float  # MHz
    power: float  # dB
    switch: bool


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

    LINE_STATUS_PATTERN = r"l(\d)F(\d+\.\d+)P(\s*[+-]?\d+\.\d+)S([01])"

    def __init__(self, driver, port):
        super().__init__(driver)

        self._port = port
        # stream r/w pair
        self._reader, self._writer = None, None

        # cached
        self._command_list = None
        self._n_channels = -1

        self._discrete_power_range = None

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

        # self._discrete_power_range = self._get_discrete_power_range()

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
        for alias, line in self._channels.items():
            aliases[line] = alias
        # find first empty slot
        for line, alias in enumerate(aliases):
            if alias is None:
                logger.debug(f'assign "{new_alias}" to line {line}')
                self._channels[new_alias] = line
                break

    ##

    def is_enabled(self, alias):
        loop = asyncio.get_event_loop()
        status = loop.run_in_executor(None, partial(self._get_line_status, alias))
        return status.switch

    async def _get_line_status(self, alias, trigger=True):
        if trigger:
            self._writer.write(f"L{self._channels[alias]}\r".encode())
            await self._writer.drain()

        status = await self._reader.readuntil(b"\r")
        status = status.decode()

        print(status)

        # parse line
        matches = re.search(self.LINE_STATUS_PATTERN, status)
        if matches:
            return LineStatus(
                frequency=float(matches.group(1)),
                power=float(matches.group(2)),
                switch=(matches.group(3) == "1"),
            )
        else:
            raise SyntaxError("unable to parse line status")

    def enable(self, alias):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._set_switch(alias, True))

    def disable(self, alias):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._set_switch(alias, False))

    ##

    async def _set_switch(self, alias, on: bool):
        print(f"{alias}, {on}")
        print(f"L{self._channels[alias]}O{int(on)}")
        self._writer.write(f"L{self._channels[alias]}O{int(on)}\r".encode())
        await self._writer.drain()

        print(f"sent, verify...")
        # verify
        status = await self._get_line_status(alias, trigger=False)
        if status.switch ^ on:
            state = "enable" if on else "disable"
            raise RuntimeError(f'unable to {state} "{alias}"')

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
            voltage (ControlVoltage): external control voltage range, either 5V max or
                10V max
        Note:
            Due to unknown reason, fast control 'V0\r' will cause the controller to
            return complete help message. Fallback to slower interactive mode, 'v\r0\r'.
        """
        await asyncio.sleep(0.5)  # slight delay to prevent message loss at MDS

        logger.debug(f"switching control voltage to {voltage.name}")
        self._writer.write(f"V{voltage.value}\r".encode())
        await self._writer.drain()
        """
        # send request
        self._writer.write(b"v\r")
        await self._writer.drain()
        # wait till user prompt
        await self._reader.readuntil(b">")
        # set mode
        self._writer.write(f"{voltage.value}\r".encode())
        await self._writer.drain()
        # wait till complete
        await self._reader.readuntil(b"?")
        """

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

