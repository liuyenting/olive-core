import logging

from olive.core import Device

__all__ = ["Galvo"]

logger = logging.getLogger(__name__)


class Galvo(Device):
    """
    A beam steering device.
    """

    def __init__(self):
        pass


class Stage(Device):
    pass


class LinearStage(Stage):
    pass


class RotaryStage(Stage):
    pass


# TODO difference between stage controller and axes, use parent
