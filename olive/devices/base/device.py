from __future__ import annotations

import asyncio
import logging
from abc import ABCMeta, abstractmethod
from typing import Tuple

from .info import DeviceInfo
from .property import (
    DEVICE_PROPERTY_CACHE_ATTR,
    is_device_property,
)

__all__ = ["Device", "DeviceType"]

logger = logging.getLogger("olive.devices")


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

        self._is_active = False

    ##

    @property
    def children(self) -> Tuple[Device]:
        return tuple(self._children)

    @property
    def driver(self):
        return self._driver

    @property
    def is_active(self):
        """
        The device or its children is selected as an concrete implementation in
        requirements.
        """
        return self._is_active or any(child.is_active for child in self._children)

    @property
    @abstractmethod
    def is_busy(self):
        """The device is not capable of actively processing new commands."""
        pass

    @property
    @abstractmethod
    def is_opened(self):
        """The host has established a connection with the device."""
        pass

    @property
    def parent(self) -> Device:
        return self._parent

    ##

    async def test_open(self):
        """
        Test open the device.

        Test open is used during enumeration, if mocking is supported, this can avoid full-scale device initialization.
        """
        try:
            await self.open()
            logger.info(f".. {await self.get_device_info()}")
        finally:
            await self.close()

    async def open(self):
        """Open the device and register with parent."""
        if not self.is_opened:
            # 1) open parent if it has one
            try:
                await self.parent.open()
            except AttributeError:
                pass

            # 2) open this device
            await self._open()

            # 3) cleanup children list
            self._children = []

        # 4) register ourself with parent
        try:
            self.parent.register(self)
        except AttributeError:
            pass

        # NOTE a device _may not_ be active, despite opened

    async def _open(self):
        """Concrete open operation."""
        raise NotImplementedError

    async def close(self, force=False):
        """
        Close the device and unregister with parent.

        Args:
            force (bool, optional): force close the device even if there are children
                still being active
        """
        if not self.is_opened:
            return

        # stop itself
        # NOTE a device _should not_ remain active, when it is not even _opened_
        self._is_active = False

        # 1) clean up children
        if self.is_active:
            # our `is_active` is already False, if we are here, this means that there
            # are active children
            logger.warning("there are still children active")
            if force:
                # 1) close all children
                results = await asyncio.gather(
                    *[child.close(force) for child in self.children],
                    return_exceptions=True,
                )
                for result in results:
                    if result is not None:
                        # something wrong happened
                        logger.exception(result)

        # 2) close ourself
        await self._close()

        # 3) unregister ourself
        try:
            self.parent.unregister(self)
        except AttributeError:
            pass

        # 4) close parent
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
        logger.debug(f'[REGISTER] DEV "{child}" -> DEV "{self}"')

        # a device must be active when it has at least 1 child
        self._is_active = True

    def unregister(self, child: Device):
        """
        Unregister a child from this device.

        Args:
            child (Device): child to remove
        """
        assert child in self._children, "child is already unregistered"
        self._children.remove(child)
        logger.debug(f'[UNREGISTER] DEV "{child}" -> DEV "{self}"')

    ##

    async def enumerate_properties(self):
        """
        Get device properties.

        If the device has not been probed before, this will causing the host to
        populate and updates the property cache.
        """
        try:
            cache_collection = getattr(self, DEVICE_PROPERTY_CACHE_ATTR)
        except AttributeError:
            # the device is not scanned yet, get the properties by probing
            return self._retrieve_device_property_names()
        else:
            return tuple(cache_collection.keys())

    async def sync(self):
        """Sync all the property cache."""
        property_names = self._retrieve_device_property_names()

        sync_tasks = [getattr(self, name).sync() for name in property_names]
        results = await asyncio.gather(*sync_tasks, return_exceptions=True)

        n_failed = 0
        for name, result in zip(property_names, results):
            if result is not None:
                try:
                    raise result
                except Exception as err:
                    print(err)
                    logger.exception(
                        f'unable to synchronize "{name}", due to "{str(err)}"'
                    )
                    n_failed += 1
        if n_failed > 0:
            logger.error(f"failed to synchronize {n_failed} properties")

    def _retrieve_device_property_names(self) -> Tuple[str]:
        """
        Test all the methods in this class, in order to figure out the decorated
        properties.
        """
        return tuple(
            name for name in dir(self) if is_device_property(getattr(self, name))
        )
