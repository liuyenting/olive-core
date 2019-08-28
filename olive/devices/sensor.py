from abc import abstractmethod

from olive.core import Device

__all__ = ['PowerMeter', 'Sensor']


class Sensor(Device):
    pass


class PowerMeter(Sensor, Device):
    @abstractmethod
    def __init__(self, driver):
        super().__init__(driver)
