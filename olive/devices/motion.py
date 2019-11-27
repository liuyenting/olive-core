from abc import abstractmethod
import asyncio
import logging
import trio
from typing import Union

from olive.core import Device

__all__ = ["Galvo", "LinearAxis", "RotaryAxis", "MotionController"]

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


class Axis(Device):
    ## position ##
    @abstractmethod
    async def home(self, blocking=True):
        pass

    @abstractmethod
    async def get_position(self):
        pass

    @abstractmethod
    async def set_absolute_position(self, pos, blocking=True):
        pass

    @abstractmethod
    async def set_relative_position(self, pos, blocking=True):
        pass

    ## velocity ##
    @abstractmethod
    async def get_velocity(self):
        pass

    @abstractmethod
    async def set_velocity(self, vel):
        pass

    ## acceleration ##
    @abstractmethod
    async def get_acceleration(self):
        pass

    @abstractmethod
    async def set_acceleration(self, acc):
        pass

    ## constraints ##
    @abstractmethod
    async def set_origin(self):
        """Define current position as the origin."""

    @abstractmethod
    async def get_limits(self):
        pass

    @abstractmethod
    async def set_limits(self):
        pass

    ## utils ##
    @abstractmethod
    async def calibrate(self):
        pass

    @abstractmethod
    async def stop(self, emergency=False):
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
