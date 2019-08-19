import logging

from .resources import DeviceManager

__all__ = ["Dispatcher"]

logger = logging.getLogger(__name__)


class Dispatcher(object):
    """
    Dispatch device confiugrations and formulate the sequence to execute on a sequencer.
    """

    def __init__(self, script):
        self._device_manager = DeviceManager()

    def eval(self):
        pass

    @property
    def device_manager(self):
        return self._device_manager
