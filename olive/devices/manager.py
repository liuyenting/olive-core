import logging
import itertools
import tempfile
from typing import Tuple

from olive.utils import Singleton, Graph
from .base import Device

__all__ = ["DeviceManager", 'query_device_hierarchy']

logger = logging.getLogger(__name__)


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    class RegisteredDevice(object):
        def __init__(self, alias, klass):
            self.alias = alias
            self.klass = klass
            self.device = None

    def __init__(self):
        # populate categories
        self._devices = {klass: [] for klass in Device.__subclasses__()}

    def set_requirements(self, requirements):
        """Device shopping list."""
        for alias, klass in requirements:
            new_device = self.RegisteredDevice(alias, klass)
            self._devices[alias] = new_device

            # map to unique identifier
            identifier = next(tempfile._get_candidate_names())
            self._devices[identifier] = new_device

    def assign(self, alias, device):
        """Link registered device to shopping list item."""
        logger.debug(f"{device} is assigned to {alias}")
        self._devices[alias].device = device

    # TODO how to cleanup register/unregister calls
    def register(self, device):
        category = device._determine_category()
        self._devices[category].append(device)
        logger.debug(f"new device {device} registered")

    def unregister(self, device):
        category = device._determine_category()
        self._devices[category].remove(device)
        logger.debug(f"{device} unregistered")

    def get_devices(self):
        return self._devices

    ##

    @property
    def devices(self) -> Tuple[Device]:
        return tuple(set(itertools.chain.from_iterable(self._devices.values())))

    @property
    def is_satisfied(self) -> bool:
        """Is the shopping list satisfied?"""
        return not any(device for device in self._devices if device.device is None)


def query_device_hierarchy():
    """
    Request function to query hierarchy for specific device.

    Returns:
        (func): a function that can find the shortest inheritance path
    """
    # build graph
    g = Graph((Device,) + Device.__subclasses__())
    for device_klass in g.nodes:
        g.add_edges(device_klass, device_klass.__subclasses__())

    def query_func(device):
        """Find the shortest path but drop the root."""
        path = g.find_path(Device, device)
        return tuple(path[1:])

    return query_func
