from __future__ import annotations
from abc import abstractmethod
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import itertools
import logging
import multiprocessing as mp
import tempfile
from typing import Tuple, NamedTuple

from olive.core.utils import Graph, Singleton

__all__ = ["Device", "DeviceInfo", "DeviceManager", "DeviceType"]

logger = logging.getLogger(__name__)

#: default thread pool uses 5 times the number of cores
MAX_WORKERS = mp.cpu_count() * 2


class DeviceInfo(NamedTuple):
    version: str
    vendor: str
    model: str
    serial_number: str

    def __repr__(self) -> str:
        if self.version:
            return f"<{self.vendor}, {self.model}, Ver={self.version}, S/N={self.serial_number}>"
        else:
            return f"<{self.vendor}, {self.model}, S/N={self.serial_number}>"


class DeviceType(type):
    """All devices belong to this type."""


class Device(metaclass=DeviceType):
    """
    All primitive device types should inherit from this class.

    Attributes:
        driver : driver that instantiate this device
        parent (Device): parent device
        timeout (int): timeout in milliseconds, None if never

    Note:
        Each device has its own thread executor to prevent external blocking calls
        block the event loop.
    """

    @abstractmethod
    def __init__(self, driver, parent: Device = None, timeout=None):
        """Abstract __init__ to prevent instantiation."""
        self._driver = driver
        self._parent, self._children = parent, []

        self._timeout = timeout

        self._executor = ThreadPoolExecutor(max_workers=1)

    """
    Device initialization.
    """

    @abstractmethod
    def test_open(self):
        """
        Test open the device.

        Test open is used during enumeration, if mocking is supported, this can avoid full-scale device initialization. This function should be _self-contained_.
        """

    def open(self):
        """Open the device and register with parent."""
        if not self.is_opened:
            # 1) open parent
            try:
                self.parent.open()
            except AttributeError:
                pass
            # 2) open ourself
            try:
                self._open()
            except NotImplementedError:
                pass
            # 3) cleanup children list
            self._children = []
        # 4) register ourself
        try:
            self.parent.register(self)
        except AttributeError:
            pass

    def _open(self):
        """Concrete open operation."""
        raise NotImplementedError

    def close(self, force=False):
        """Close the device and unregister with parent."""
        if not self.is_opened:
            return

        if self.children:
            logger.warning("there are still children active")
            if not force:
                return
        # 4) unregister ourself
        try:
            self.parent.unregister(self)
        except AttributeError:
            pass
        # 3) cleanup children list, ignored
        # 2) close ourself
        try:
            self._close()
        except NotImplementedError:
            pass
        # 1) close parent
        try:
            self.parent.close()
        except AttributeError:
            pass

    def _close(self):
        """Concrete close operation."""
        raise NotImplementedError

    def register(self, child):
        self._children.append(child)
        logger.debug(f'"{child.info}" registered')

    def unregister(self, child):
        try:
            self._children.remove(child)
            logger.debug(f'"{child.info}" unregistered')
        except ValueError:
            raise ValueError(
                "children was prematurely removed from watch list, please file an issue"
            )

    """
    Device properties.
    """

    @abstractmethod
    def enumerate_properties(self):
        """Get properties supported by the device."""

    def get_property(self, name):
        """
        Get the value of device property.

        Args:
            name (str): documented property name
            value : new value of the specified property
        """
        func = self._get_accessor("_get", name)
        return func()

    def set_property(self, name, value):
        """
        Set the value of device property.

        Args:
            name (str): documented property name
        """
        func = self._get_accessor("_set", name)
        func(value)

    def _get_accessor(self, prefix, name):
        try:
            return getattr(self, f"{prefix}_{name}")
        except AttributeError:
            try:
                return getattr(self.parent, f"{prefix}_{name}")
            except AttributeError:
                raise AttributeError(f'unknown property "{name}"')

    """
    Driver-device associations.
    """

    @property
    def children(self):
        return tuple(self._children)

    @property
    def driver(self):
        return self._driver

    @property
    @abstractmethod
    def is_opened(self):
        """Is the device opened?"""

    @property
    def parent(self) -> Device:
        return self._parent

    """
    Exceution.
    """

    @property
    @abstractmethod
    def busy(self) -> bool:
        """Is device busy?"""

    @property
    def executor(self):
        return self._executor

    @property
    @abstractmethod
    def info(self) -> DeviceInfo:
        """Return device info."""

    @property
    def timeout(self):
        """Device timeout in milliseconds."""
        return self._timeout


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
