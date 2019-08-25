import logging

from olive.devices import Camera

__all__ = ["PseudoCamera"]

logger = logging.getLogger(__name__)


class PseudoCamera(Camera):
    def __init__(self):
        super().__init__()

    @classmethod
    def discover(cls):
        pass

    def initialize(self):
        super().initialize()

    def close(self):
        super().close()

    def enumerate_attributes(self):
        pass

    def get_attribute(self, name):
        pass

    def set_attribute(self, name, value):
        pass

