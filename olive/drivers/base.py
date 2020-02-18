import logging
from abc import ABCMeta, abstractmethod
import asyncio
from typing import Iterable, get_type_hints

from olive.devices.base import Device, DeviceType

__all__ = ["Driver", "DriverType"]

logger = logging.getLogger(__name__)


class DriverType(ABCMeta):
    """All drivers belong to this type."""


class Driver(metaclass=DriverType):
    def __init__(self):
        self._devices = []

    ##

    @property
    def is_active(self):
        return any(device.is_opened() for device in self._devices)

    ##

    @abstractmethod
    def initialize(self):
        """Initialize the library."""

    @abstractmethod
    def shutdown(self):
        """Cleanup resources allocated by the library."""

    ##

    async def enumerate_devices(self, no_cache=False) -> Iterable[Device]:
        """
        List devices that this driver can interact with.

        Args:
            no_cache (bool, optional): always request new hardware list

        Note:
            Returned devices are NOT active yet.
        """
        candidates = await self._enumerate_devices()

        # ignore devices that are already active
        active_devices = [device for device in self._devices if device.is_opened()]
        logger.debug(
            f"there are {len(active_devices)} active device(s) during enumeration"
        )
        candidates = [device for device in candidates if device not in active_devices]

        inactive_devices = []
        if candidates:
            # test device support
            tasks = [device.test_open() for device in candidates]
            results = await asyncio.gather(*tasks, return_exception=True)

            for device, result in zip(candidates, results):
                if result is None:
                    inactive_devices.append(result)

        # combine results and refresh internal book-keeping
        self._devices = active_devices + inactive_devices

        return self._devices

    @abstractmethod
    async def _enumerate_devices(self) -> Iterable[Device]:
        """
        Enumerate possible devices, but _not_ tested for compatibility.

        Note:
            Returned devices are _not_ tested nor active.
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
