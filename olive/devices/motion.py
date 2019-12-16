from abc import abstractmethod
from enum import auto, Enum
import logging
from typing import Union

from olive.core import Device

__all__ = ["Galvo", "LimitStatus", "LinearAxis", "RotaryAxis", "MotionController"]

logger = logging.getLogger(__name__)


class Galvo(Device):
    """
    A beam steering device.
    """

    # TODO galvo REQUIRES sequencer waveform support
    @abstractmethod
    def __init__(self):
        pass

    ##

    def get_table_size(self):
        pass

    def get_waveform(self):
        pass

    def set_waveform(self):
        pass

    ##

    def get_amplitude_range(self):
        pass

    def get_amplitude(self):
        pass

    def set_amplitude(self):
        pass

    def get_offset(self):
        pass

    def set_offset(self):
        pass

    def get_frequency(self):
        pass

    def set_frequency(self):
        pass

    def get_phase_shift(self):
        pass

    def set_phase_shift(self):
        pass


class LimitStatus(Enum):
    WithinRange = auto()
    UpperLimit = auto()
    LowerLimit = auto()


class Axis(Device):
    ## position ##
    @abstractmethod
    async def go_home(self, blocking=True):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    async def move_absolute(self, pos, blocking=True):
        pass

    @abstractmethod
    async def move_relative(self, pos, blocking=True):
        pass

    @abstractmethod
    def move_continuous(self, vel):
        pass

    ## velocity ##
    @abstractmethod
    def get_velocity(self):
        pass

    @abstractmethod
    def set_velocity(self, vel):
        pass

    ## acceleration ##
    @abstractmethod
    def get_acceleration(self):
        pass

    @abstractmethod
    def set_acceleration(self, acc):
        pass

    ## constraints ##
    @abstractmethod
    def set_origin(self):
        """Define current position as the origin."""

    @abstractmethod
    def get_limits(self):
        pass

    @abstractmethod
    def get_limit_status(self) -> LimitStatus:
        pass

    @abstractmethod
    def set_limits(self):
        pass

    ## utils ##
    @abstractmethod
    async def calibrate(self):
        pass

    @abstractmethod
    def stop(self, emergency=False):
        pass

    @abstractmethod
    async def wait(self):
        pass


class LinearAxis(Axis, Device):
    """
    Linear axis is a component of a precise motion system used to restrict an object
    to a single axis of _translation_.
    """


class RotaryAxis(Axis, Device):
    """
    A rotary axis is a component of a motion system used to restrict an object to a single axis of _rotation_.
    """


class MotionController(Device):
    @abstractmethod
    async def enumerate_axes(self) -> Union[Axis]:
        """Enumerate connected axes."""
