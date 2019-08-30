from abc import abstractmethod

from olive.core import Device

__all__ = ["Sensor", "SensorAdapter", "PowerSensor"]


class SensorAdapter(Device):
    """
    A sensor adapter provides physical interface between computer and the sensor.
    """


class Sensor(Device):
    """
    A device, module, or subsystem whose purpose is to detect events or changes in its
    environment and send the information to processors.
    """

    @abstractmethod
    def __init__(self, driver, parent: SensorAdapter = None):
        super().__init__(driver, parent=parent)


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
