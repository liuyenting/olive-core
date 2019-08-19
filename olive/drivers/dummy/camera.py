import logging

from olive.devices import Camera

__all__ = ["DummyCamera"]

logger = logging.getLogger(__name__)


class DummyCamera(Camera):
    def __init__(self):
        super().__init__()
