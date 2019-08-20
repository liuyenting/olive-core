import logging

from olive.devices import Camera

__all__ = ["PseudoCamera"]

logger = logging.getLogger(__name__)


class PseudoCamera(Camera):
    def __init__(self):
        super().__init__()
