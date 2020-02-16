import logging
from abc import ABCMeta, abstractmethod
from typing import Iterable, get_type_hints

from olive.devices.base import Device, DeviceType

__all__ = ["Driver", "DriverType"]

logger = logging.getLogger(__name__)


class DriverType(ABCMeta):
    """All drivers belong to this type."""


class Driver(metaclass=DriverType):
    def __init__(self):
        self._active_devices = []

    ##

    @property
    def active_devices(self) -> Iterable[Device]:
        return tuple(self._active_devices)

    @property
    def is_active(self):
        return len(self._active_devices) > 0

    ##

    @abstractmethod
    def initialize(self):
        """Initialize the library."""

    @abstractmethod
    def shutdown(self):
        """Cleanup resources allocated by the library."""

    ##

    def register(self, device: Device):
        assert (
            device not in self._active_devices
        ), "device is already registered, something wrong with the initialize process"
        self._active_devices.append(device)
        logger.debug(f'[REG] DEV "{device}" -> DRV "{self}"')

    def unregister(self, device: Device):
        assert (
            device in self._active_devices
        ), "device is already unregistered, something wrong with the shutdown process"
        self._active_devices.remove(device)
        logger.debug(f'[UNREG] DEV "{device}" -> DRV "{self}"')

    ##

    @abstractmethod
    async def enumerate_devices(self) -> Iterable[Device]:
        """
        List devices that this driver can interact with.

        Note:
            Returned devices are NOT active yet.
        """

    @classmethod
    def enumerate_supported_device_types(cls) -> Iterable[DeviceType]:
        """List device types that this driver may support."""
        hints = get_type_hints(cls.enumerate_devices)["return"]
        try:
            klasses = hints.__args__
        except AttributeError:
            # not an iterable
            klasses = [hints]

        # remap to device primitives
        device_klasses = []
        for klass in klasses:
            device_klasses.extend(klass.__bases__)
        return tuple(set(device_klasses) & set(Device.__subclasses__()))
