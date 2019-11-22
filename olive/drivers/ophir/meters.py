from abc import abstractmethod
import asyncio
from itertools import product
import logging
from typing import Union

from serial import Serial
from serial.tools import list_ports

from olive.core import Driver, DeviceInfo
from olive.core.utils import retry
from olive.devices import SensorAdapter
from olive.devices.errors import UnsupportedDeviceError

from olive.drivers.ophir.sensors import Photodiode

__all__ = ["Ophir", "Nova2"]

logger = logging.getLogger(__name__)


class OphirMeter(SensorAdapter):
    """
    Base class for Ophir power meters.

    Args:
        port (str): device name
        baudrate (int): baud rate
        timeout (int): timeout in ms
    """

    def __init__(self, driver, port, baudrate, timeout=1000):
        super().__init__(driver, timeout=timeout)

        # Serial use s instead of ms
        timeout = self.timeout
        if timeout is not None:
            timeout /= 1000

        ser = Serial()
        ser.port = port
        ser.baudrate = baudrate
        ser.timeout = timeout
        ser.write_timeout = timeout
        self._handle = ser

    def enumerate_sensors(self) -> Union[Photodiode, None]:
        self.handle.write(b"$HT\r")
        response = self.handle.read_until("\r").decode("utf-8")
        # LaserStar and Nova-II append the measurement, split them by space
        response = response.strip("* ").split()[0]
        try:
            return ({"SI": Photodiode, "XX": None}[response],)
        except KeyError:
            raise RuntimeError(f'unknown head type "{response}"')

    ##

    def enumerate_properties(self):
        return tuple()

    ##

    @property
    def busy(self):
        return False

    @property
    def handle(self):
        return self._handle

    @property
    def info(self) -> DeviceInfo:
        # mode name and serial number
        self.handle.write(b"$II\r")
        try:
            response = self.handle.read_until("\r").decode("utf-8")
            _, sn, name = tuple(response.strip("* ").split())
        except (ValueError, UnicodeDecodeError):
            raise SyntaxError("unable to parse device info")

        # ROM version
        self.handle.write(b"$VE\r")
        response = self.handle.read_until("\r").decode("utf-8")
        version = response.strip("* ").split()[0]

        return DeviceInfo(version=version, vendor="Ophir", model=name, serial_number=sn)

    @property
    def is_opened(self):
        return self.handle.is_open

    """
    Property accessors.
    """

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
        self.handle.write(b"$IC\r")
        response = self.handle.read_until("\r").decode("utf-8")
        if response[0] == "?":
            raise RuntimeError("failed to save instrument configuration")


class Nova2(OphirMeter):
    """
    Handheld Laser Power & Energy Meter. P/N 7Z01550.

    Compatible with all standard Ophir Thermopile, BeamTrack, Pyroelectric and Photodiode sensors.
    """

    @retry(UnsupportedDeviceError, logger=logger)
    def test_open(self):
        self.handle.open()
        try:
            logger.info(f".. {self.info}")
        except SyntaxError:
            raise UnsupportedDeviceError
        finally:
            # fast close
            self.handle.close()

    def open(self):
        self.handle.open()
        self._set_full_duplex()

    def close(self):
        # no more children
        self._save_configuration()
        self.handle.close()

    ##

    def enumerate_properties(self):
        return super().enumerate_properties()

    ##

    # TODO power meter related operations

    ##

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

    def enumerate_devices(self) -> Union[Photodiode, None]:
        loop = asyncio.get_event_loop()

        async def test_device(device):
            """Test each port using their own thread."""

            def _test_device(device):
                logger.debug(f"testing {device.handle.name}...")
                device.test_open()

            return await loop.run_in_executor(device.executor, _test_device, device)

        klasses = OphirMeter.__subclasses__()
        baudrates = (38400, 19200, 9600)
        ports = [info.device for info in list_ports.comports()]

        logger.info("looking for controllers...")
        # each port can only test 1 combination at once
        controllers = []
        for klass, baudrate in product(*[klasses, baudrates]):
            logger.debug(f"combination {klass} ({baudrate} bps)")
            _controllers = [klass(self, port, baudrate) for port in ports]
            testers = asyncio.gather(
                *[test_device(controller) for controller in _controllers],
                return_exceptions=True,
            )
            results = loop.run_until_complete(testers)

            for controller, result in zip(_controllers, results):
                if isinstance(result, UnsupportedDeviceError):
                    continue
                elif result is None:
                    # remove from test cycle
                    ports.remove(controller.handle.port)
                    controllers.append(controller)
                else:
                    # unknown exception occurred
                    raise result

        logger.info("interrogating controllers...")
        valid_sensors = []
        # scan each controller for their connected sensor
        for controller in controllers:
            # temporary open the controller
            controller.open()
            # retrieve sensor devices
            _sensors = [klass(controller) for klass in controller.enumerate_sensors()]
            # close the controller
            controller.close()

            # test the sensor candidates
            testers = asyncio.gather(
                *[test_device(sensor) for sensor in _sensors], return_exceptions=True
            )
            results = loop.run_until_complete(testers)

            for sensor, result in zip(_sensors, results):
                if isinstance(result, UnsupportedDeviceError):
                    continue
                elif result is None:
                    valid_sensors.append(sensor)
                else:
                    # unknown exception occurred
                    raise result

        return tuple(valid_sensors)
