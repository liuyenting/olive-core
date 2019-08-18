import logging

from olive.devices import Camera

logger = logging.getLogger(__name__)


class DummyCamera(Camera):
    def __init__(self):
        super().__init__()
