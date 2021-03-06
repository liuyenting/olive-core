from __future__ import annotations

import logging
from abc import ABCMeta, abstractmethod
from typing import NamedTuple, Tuple

__all__ = ["Device", "DeviceInfo", "DeviceType"]

logger = logging.getLogger(__name__)


class DeviceInfo(NamedTuple):
    version: str = ""
    vendor: str = ""
    model: str = ""
    serial_number: str = ""

    def __repr__(self) -> str:
        tokens = [
            ("", self.vendor),
            ("", self.model),
            ("version=", self.version),
            ("s/n=", self.serial_number),
        ]
        tokens[:] = [f"{name}{value}" for name, value in tokens if len(value) > 0]
        return f"<{', '.join(tokens)}>"


class DeviceType(ABCMeta):
    """All devices belong to this type."""


class Device(metaclass=DeviceType):
    """
    All primitive device types should inherit from this class.

    Args:
        driver : driver that instantiate this device
        parent (Device): parent device
    """

    def __init__(self, driver, *, parent: Device = None):
        """Abstract __init__ to prevent instantiation."""
        self._driver = driver
        self._parent, self._children = parent, []

        self._info = None

    ##

    @property
    def children(self) -> Tuple[Device]:
        return tuple(self._children)

    @property
    def driver(self):
        return self._driver

    @property
    def parent(self) -> Device:
        return self._parent

    ##

    @abstractmethod
    async def test_open(self):
        """
        Test open the device.

        Test open is used during enumeration, if mocking is supported, this can avoid full-scale device initialization.
        """

    async def open(self):
        """Open the device and register with parent."""
        if not self.is_opened:
            # 1) open parent if it has one
            try:
                await self.parent.open()
            except AttributeError:
                pass
            try:
                # 2) open this device
                await self._open()
            except NotImplementedError:
                pass
            # 3) cleanup children list
            self._children = []
        # 4) register ourself with parent
        try:
            self.parent.register(self)
        except AttributeError:
            pass
        # 5) get device info

    async def _open(self):
        """Concrete open operation."""
        raise NotImplementedError

    async def close(self, force=False):
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
            await self._close()
        except NotImplementedError:
            pass
        # 1) close parent
        try:
            await self.parent.close()
        except AttributeError:
            pass

    async def _close(self):
        """Concrete close operation."""
        raise NotImplementedError

    ##

    @abstractmethod
    async def get_device_info(self) -> DeviceInfo:
        """Get device info after a successful init."""

    ##

    def register(self, child: Device):
        """
        Register a child to this device.

        Args:
            child (Device): child to add
        """
        assert child not in self._children, "child is already registered"
        self._children.append(child)
        logger.debug(f'[REG] DEV "{child}" -> DEV "{self}"')

    def unregister(self, child: Device):
        """
        Unregister a child from this device.

        Args:
            child (Device): child to remove
        """
        assert child in self._children, "child is already unregistered"
        self._children.remove(child)
        logger.debug(f'[UNREG] DEV "{child}" -> DEV "{self}"')

    ##

    @abstractmethod
    async def enumerate_properties(self):
        """Get properties supported by the device."""

    async def get_property(self, name):
        """
        Get the value of device property.

        Args:
            name (str): documented property name
            value : new value of the specified property
        """
        try:
            func = self._get_accessor("_get", name)
            return await func()
        except AttributeError:
            return self.parent.get_property(name)

    async def set_property(self, name, value):
        """
        Set the value of device property.

        Args:
            name (str): documented property name
        """
        try:
            func = self._get_accessor("_set", name)
            await func(value)
        except AttributeError:
            self.parent.set_property(name, value)

    def _get_accessor(self, prefix, name):
        try:
            return getattr(self, f"{prefix}_{name}")
        except AttributeError:
            raise AttributeError(f'unknown property "{name}"')
