from abc import ABCMeta
from collections import defaultdict
import logging
from typing import Tuple
from uuid import uuid4 as uuid

from olive.core.utils import Singleton


__all__ = ["DeviceManager"]

logger = logging.getLogger(__name__)


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        logger.debug("Device Manager initiated")

        self._devices = defaultdict(list)

    def add_device(self, device):
        self._devices[uuid().hex] = device

    def get_devices(self):
        return self._devices

    @property
    def devices(self) -> Tuple[ABCMeta]:
        pass
