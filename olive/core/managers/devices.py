import itertools
import logging
import tempfile
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Type

from olive.devices.base import Device
from olive.utils import Graph, Singleton

__all__ = ["DeviceManager", "query_device_hierarchy"]

logger = logging.getLogger(__name__)


@dataclass
class RequirementEntry:
    dtype: Type[Device]
    instance: Optional[Device] = None


class Requirements(MutableMapping):
    def __init__(self, requirements: Dict[str, Device]):
        self._requirements = {
            alias: RequirementEntry(device_klass)
            for alias, device_klass in requirements.items()
        }

    def __getitem__(self, alias) -> Device:
        return self._requirements[alias].instance

    def __setitem__(self, alias, device: Device):
        dtype = self._requirements[alias].dtype
        assert isinstance(device, dtype), f'"{device}" does not belong to "{dtype}"'
        self._requirements[alias].instance = device

    def __delitem__(self, alias):
        self._requirements[alias].instance = None

    def __iter__(self):
        for alias in self._requirements.keys():
            yield alias

    def __len__(self):
        return len(self._requirements)

    ##

    @property
    def is_satisfied(self):
        return all(device is not None for device in self.values())

    ##

    # TODO implement update reuqirement


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.
    """

    def __init__(self):
        self._requirements = None  # TODO WIP

    ##

    @property
    def devices(self) -> Tuple[Device]:
        return tuple(set(itertools.chain.from_iterable(self._devices.values())))

    @property
    def is_satisfied(self) -> bool:
        """Is the shopping list satisfied?"""
        return not any(device for device in self._devices if device.device is None)

    @property
    def requirements(self) -> Requirements:
        return self._requirements

    ##

    def update_requirements(self, requirements):
        self._requirements

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
