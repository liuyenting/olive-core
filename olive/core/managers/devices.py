import itertools
import logging
import uuid
from collections.abc import MutableMapping
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Type, Iterable

from olive.devices.base import Device
from olive.utils import Graph, Singleton

__all__ = ["DeviceManager", "Requirements", "query_device_hierarchy"]

logger = logging.getLogger(__name__)


@dataclass
class RequirementEntry:
    dtype: Type[Device]
    instance: Optional[Device] = None


class Requirements(MutableMapping):
    """
    Book-keeping device requirements.

    This class records associations between alias and its required device type. If
    assigned, also its linked concrete device instance.

    Args:
        requirements (dict of str: Device, optional): desired alias-device requirements
    """

    def __init__(self, requirements: Optional[Dict[str, Device]] = None):
        self._requirements = dict()
        try:
            self._requirements.update(
                {
                    alias: RequirementEntry(device_klass)
                    for alias, device_klass in requirements.items()
                }
            )
        except AttributeError:
            logger.debug(f"empty requirements")

    def __getitem__(self, alias) -> Device:
        return self._requirements[alias].instance

    def __setitem__(self, alias, device: Device):
        # ensure the slot is empty
        assert (
            self._requirements[alias].instance is None
        ), f'please unlink "{alias}" first'

        # ensure device is correct
        dtype = self._requirements[alias].dtype
        assert isinstance(device, dtype), f'"{device}" does not belong to "{dtype}"'

        # save it
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

    def update(self, new_req: Dict[str, Device]) -> Iterable[Device]:
        """
        Update requirements and re-use existing alias-device association if possible.

        Args:
            new_req (dict of str: Device): new requirements

        Returns:
            (list of Device): devices not required in new requirements

        Notes:
            Unused devices may still be active. Remember to close them afterward.
        """
        merged = dict()

        # keep alias that has the same dtype
        device_to_rm = []
        for alias, entry in self.items():
            try:
                new_dtype = new_req[alias]
                if entry.dtype == new_dtype:
                    logger.debug(f'keep "{alias}" ({entry.dtype})')
                    merged[alias] = entry
                else:
                    logger.debug(f'"{alias}" changes type to "{new_dtype}"')
                    merged[alias] = RequirementEntry(new_dtype)
            except KeyError:
                logger.debug(f'drop "{alias}" ({new_dtype})')
                device_to_rm.append(entry.instance)

        # add new requirements
        new_aliases = set(new_req.keys()) - set(merged.keys())
        for alias in new_aliases:
            new_dtype = new_req[alias]
            logger.debug(f'new entry "{alias}" ({new_dtype})')
            merged[alias] = RequirementEntry(new_dtype)

        # replace
        self._requirements = merged

        return device_to_rm


class DeviceManager(metaclass=Singleton):
    """
    Device bookkeeping.

    # FIXME
    >> registration flow
    1) instantiate new device
    2) register device
    --
    2.1) open device
    2.2) save device to internal list
    --
    5) update requirements
    --
    5.1) try to assign device
    5.2) cleanup unused devices

    """

    def __init__(self):
        self._requirements = Requirements()
        self._devices = []

    ##

    @property
    def devices(self) -> Tuple[Device]:
        """Monitored devices."""
        return tuple(self._devices)

    @property
    def is_satisfied(self) -> bool:
        """Is the shopping list satisfied?"""
        return not any(device for device in self._devices if device.device is None)

    ##

    def register(self, device: Device):
        """
        Register and open a device.

        Args:
            device (Device): new device
        """
        logger.debug(f'[REG] "{device}"')
        # TODO device.open
        self._devices.append(device)

    def unregister(self, device: str):
        """
        Unregister and close a device.

        Args:
            device (Device): device to unregister
        """
        logger.debug(f'[UNREG] "{device}"')
        assert device in self._devices, f'"{device}" is not registered'
        # TODO device.close
        self._devices.remove(device)

    ##

    def update_requirements(self, requirements: Dict[str, Device]):
        """
        Update requirements and re-use existing alias-device association if possible.

        Args:
            new_req (dict of str: Device): new requirements
        """
        unused_devices = self._requirements.update(requirements)
        logger.debug(
            f"{len(unused_devices)} device(s) are not required after the update"
        )
        for device in unused_devices:
            self.unregister(device)

    def link(self, alias: str, device: Device):
        """
        Link registered device to shopping list item.

        Args:
            alias (str): alias of the device to link with
            device (Device): the concrete device instance
        """
        logger.debug(f'[LINK] "{device}" -> "{alias}')
        self._requirements[alias] = device
        self.register(device)

    def unlink(self, alias: str):
        """
        Unlink alias-device association.

        Args:
            alias (str): alias of the device to unlink
        """
        logger.debug(f'[UNLINK] "{alias}"')
        device = self._requirements.pop(alias)
        self.unregister(device)

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
