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
import logging

from olive.devices import PowerSensor

__all__ = ["Photodiode"]

logger = logging.getLogger(__name__)


class Photodiode(PowerSensor):
    """
    Photodiode sensors have a high degree of linearity over a large range of light
    power levels.
    """

    def __init__(self, driver, parent):
        if parent is None:
            raise TypeError("parent device is required")
        super().__init__(driver, parent=parent)
        self._handle = self.parent.handle

    ##

    def open(self):
        pass

    def close(self):
        pass

    ##

    def enumerate_properties(self):
        return ("supported_wavelength",)

    ##

    def get_reading(self):
        pass

    def set_wavelength(self):
        self.parent.handle.write(b"")

    ##

    @property
    def handle(self):
        return self._handle

    """
    Property accessors.
    """

    def _get_supported_wavelength(self):
        self.handle.write(b"$AW\r")
        response = self.handle.read_until("\r").decode("utf-8")
        mode, *args = tuple(response.strip("* ").split(" "))
        if mode == "CONTINUOUS":
            fmin, fmax, *options = tuple(args)
            return (fmin, fmax)
        elif mode == "DISCRETE":
            _, *options = tuple(args)
            return options
        else:
            raise RuntimeError(f'unknown mode "{mode}""')
