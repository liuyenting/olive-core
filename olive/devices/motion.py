from abc import abstractmethod
import logging

from olive.core import Device

__all__ = ["Galvo", "Stage", "LinearStage", "RotaryStage", "MotionController"]

logger = logging.getLogger(__name__)


class Galvo(Device):
    """
    A beam steering device.
    """

    def __init__(self):
        pass


class Stage(Device):
    @abstractmethod
    def __init__(self, driver, parent):
        super().__init__(driver, parent)


class LinearStage(Stage, Device):
    """
    Linear stage is a component of a precise motion system used to restrict an object
    to a single axis of _translation_.
    """

    @abstractmethod
    def __init__(self, driver, parent):
        super().__init__(driver, parent)


class RotaryStage(Stage, Device):
    """
    A rotary stage is a component of a motion system used to restrict an object to a single axis of _rotation_.
    """

    @abstractmethod
    def __init__(self, driver, parent):
        super().__init__(driver, parent)


class MotionController(Device):
    pass
