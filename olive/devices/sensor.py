from abc import abstractmethod
import logging

from olive.core import Device

__all__ = []

class Sensor(Device):
    pass

class PowerMeter(Sensor, Device):
    @abstractmethod
    def __init__(self, driver):
        super().__init__(driver)
