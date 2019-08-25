import itertools
import logging
from typing import Tuple
from uuid import uuid4 as uuid_gen

from olive.core.utils import Singleton
from olive.devies.base import Device

__all__ = ["DeviceManager"]

logger = logging.getLogger(__name__)


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        # populate categories
        self._devices = {klass: [] for klass in Device.__subclasses__()}

    def register(self, device):
        new_uuid = uuid_gen().bytes
        self._devices[new_uuid] = device
        logger.debug(f'new device {device} registered as "{new_uuid}"')

    def unregister(self, device):
        uuid = device.uuid
        # TODO remove entry by UUID
        # TODO detroy the device

    def get_devices(self):
        return self._devices

    @property
    def devices(self) -> Tuple[Device]:
        return tuple(itertools.chain.from_iterable(self._devices.values()))
