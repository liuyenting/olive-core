"""
Ophir offers a complete range of laser power and energy sensors measuring femtowatts to hundreds of kilowatts and picojoules to hundreds of joules.

According to the manual, there are 8 types of head:
- Thermopile
- BC20
- Temperature probe
- Photodiode
- CIE head
- RP head
- Pyroelectric
- nanoJoule meter
"""
from enum import Enum
from functools import lru_cache
import logging

from olive.core import DeviceInfo
from olive.core.utils import retry
from olive.devices import PowerSensor
from olive.devices.errors import UnsupportedDeviceError

__all__ = ["Photodiode", "DiffuserSetting"]

logger = logging.getLogger(__name__)


class DiffuserSetting(Enum):
    FILTER_OUT = "1"
    FILTER_IN = "2"


class WavelengthSupport(Enum):
    CONTINUOUS = "CONTINUOUS"
    DISCRETE = "DISCRETE"


class Photodiode(PowerSensor):  # TODO extract common scheme to OphirSensor
    """
    Photodiode sensors have a high degree of linearity over a large range of light
    power levels.
    """

    def __init__(self, parent):
        super().__init__(parent.driver, parent=parent)
        self._handle = self.parent.handle

    ##

    @retry(UnsupportedDeviceError, logger=logger)
    def test_open(self):
        self.handle.open()
        try:
            logger.info(f".. {self.info}")
        except SyntaxError:
            raise UnsupportedDeviceError
        finally:
            self.handle.close()

    def open(self):
        # using a power sensor, auto switch to 'Power screen'
        self.handle.write(b"$FP\r")
        self.handle.read_until("\r")

        super().open()

    def close(self):
        super().close()

    ##

    def enumerate_properties(self):
        return ("diffuser", "favorite_wavelengths", "valid_wavelengths")

    ##

    def readout(self):
        self.handle.write(b"$SP\r")
        response = self.handle.read_until("\r").decode("utf-8")
        try:
            return float(response.strip("* "))
        except ValueError:
            if "OVER" in response:
                raise ValueError("sensor reading out-of-range")

    def get_current_range(self):
        valid_ranges = self.get_valid_ranges()

        self.handle.write(b"$RN\r")
        response = self.handle.read_until("\r").decode("utf-8")
        # since index of AUTO is 1, and dBm is 2, subscript needs to be offset by 2
        index = int(response.strip("* ")) + 2
        return valid_ranges[index]

    def set_current_range(self, value):
        valid_ranges = self.get_valid_ranges()
        try:
            # since index of AUTO is 1, and dBm is 2, subscript needs to be offset by 2
            index = valid_ranges.index(value) - 2
        except ValueError:
            raise ValueError("invalid range")
        self.handle.write(f"$WN{index}\r".encode())
        response = self.handle.read_until("\r").decode("utf-8")
        if response[0] != "*":
            raise RuntimeError("unable to set range")

    def get_unit(self):
        self.handle.write(b"$SI\r")
        response = self.handle.read_until("\r").decode("utf-8")
        unit = response.strip("* ").split()[0]
        try:
            # some units use abbreviations
            return {"d": "dBm", "l": "lux", "c": "fc"}[unit]
        except KeyError:
            return unit

    @lru_cache(maxsize=1)
    def get_valid_ranges(self):
        logger.debug("get_valid_ranges(), probing")
        self.handle.write(b"$AR\r")
        response = self.handle.read_until("\r").decode("utf-8")
        _, *options = tuple(response.strip("* ").split())
        return tuple(options)

    def set_wavelength(self, value):
        mode, options = self._get_valid_wavelengths()
        if mode == WavelengthSupport.CONTINUOUS:
            fmin, fmax = options
            if value < fmin or value > fmax:
                raise ValueError(f"wavelength {value} out-of-range")
            self.handle.write(f"$WL{value}\r".encode())
        elif mode == WavelengthSupport.DISCRETE:
            if value not in options:
                raise ValueError(f"unknown wavelength setting {value}")
            self.handle.write(f"$WW{value}\r".encode())
        response = self.handle.read_until("\r").decode("utf-8")
        if response[0] != "*":
            raise RuntimeError("unable to set range")

    ##

    @property
    def busy(self):
        return self.parent.busy

    @property
    def handle(self):
        return self._handle

    @property
    def info(self) -> DeviceInfo:
        self.handle.write(b"$HI\r")
        try:
            response = self.handle.read_until("\r").decode("utf-8")
            _, sn, name, _ = tuple(response.strip("* ").split())
        except (ValueError, UnicodeDecodeError):
            raise SyntaxError("unable to parse device info")
        return DeviceInfo(version=None, vendor="Ophir", model=name, serial_number=sn)

    """
    Property accessors.
    """

    def _get_diffuser(self):
        self.handle.write(b"$FQ0\r")
        response = self.handle.read_until("\r").decode("utf-8")
        mode, *options = tuple(response.strip("* ").split())
        return DiffuserSetting(mode)

    def _set_diffuser(self, setting: DiffuserSetting):
        self.handle.write(f"$FQ{setting.value}\r".encode())
        response = self.handle.read_until("\r").decode("utf-8")
        mode = response.strip("* ").split()[0]
        try:
            DiffuserSetting(mode)
        except ValueError:
            raise ValueError(f"failed to set diffuser property ({setting})")

    def _get_favorite_wavelengths(self):
        self.handle.write(b"$AW\r")
        response = self.handle.read_until("\r").decode("utf-8")
        mode, *args = tuple(response.strip("* ").split())
        try:
            mode = WavelengthSupport(mode)
            if mode == WavelengthSupport.DISCRETE:
                raise RuntimeError("DISCRETE head does not support favorite wavelength")
            return tuple(args[3:])
        except ValueError:
            raise ValueError(f'unknown mode "{mode}"')

    @lru_cache(maxsize=1)
    def _get_valid_wavelengths(self):
        self.handle.write(b"$AW\r")
        response = self.handle.read_until("\r").decode("utf-8")
        mode, *args = tuple(response.strip("* ").split())
        try:
            mode = WavelengthSupport(mode)
            if mode == WavelengthSupport.CONTINUOUS:
                fmin, fmax, *options = tuple(args)
                options = (int(fmin), int(fmax))
            elif mode == WavelengthSupport.DISCRETE:
                _, *options = tuple(args)
            return mode, options
        except ValueError:
            raise ValueError(f'unknown mode "{mode}"')

    """
    Private helper functions and constants.
    """

