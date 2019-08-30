from abc import abstractmethod
from typing import Union

from olive.core import Device

__all__ = ["Sensor", "SensorAdapter", "PowerSensor"]


class Sensor(Device):
    """
    A device, module, or subsystem whose purpose is to detect events or changes in its
    environment and send the information to processors.

    Note:
        If parent exists, they should be the one handling open and closing, since they
        are already aware of this sensor during enumeration.
    """

    @abstractmethod
    def __init__(self, driver, parent: "SensorAdapter" = None):
        super().__init__(driver, parent=parent)

    ##

    def open(self):
        if self.parent:
            self.parent.open()
        super().open()

    def close(self):
        if self.parent:
            self.parent.close()
        super().close()


class SensorAdapter(Device):
    """
    A sensor adapter provides physical interface between computer and the sensor.
    """

    @abstractmethod
    def enumerate_sensors(self) -> Union[Sensor]:
        """ENumerate connected sensors."""


##


class PowerSensor(Sensor):
    """
    Power sensor is a detector that absorbs a laser beam and outputs a signal
    proportional to the beam’s power, _usually_ calibrated with a defined accuracy to a
    specified standard and used as the input of a power meter.
    """

    @abstractmethod
    def get_reading(self):
        """Get power reading from the sensor."""

    @abstractmethod
    def set_wavelength(self):
        """Configure the wavelength to work with."""
