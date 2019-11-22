from abc import abstractmethod
import logging
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
    @abstractmethod
    def home(self):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def set_absolute_position(self):
        pass

    @abstractmethod
    def set_relative_position(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    ## constraints
    @abstractmethod
    def set_origin(self):
        """Define current position as the origin."""

    @abstractmethod
    def get_limits(self):
        pass

    @abstractmethod
    def set_limits(self):
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
    def enumerate_axes(self) -> Union[Axis]:
        """Enumerate connected axes."""
