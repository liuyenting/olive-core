import asyncio
import logging
from abc import ABCMeta, abstractmethod
from typing import Iterable, Tuple, get_type_hints

from olive.devices.base import Device, DeviceType
from olive.devices.error import UnsupportedClassError

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

    def initialize(self):
        """Initialize the library."""

    def shutdown(self):
        """Cleanup resources allocated by the library."""
        for device in self._devices:
            device.close()

    ##

    async def enumerate_devices(self) -> Tuple[Device]:
        """
        List devices that this driver can interact with.

        Note:
            Returned devices are NOT active yet.
        """
        candidates = self._enumerate_device_candidates()

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
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for device, result in zip(candidates, results):
                if result is None:
                    inactive_devices.append(device)
                else:
                    try:
                        raise result
                    except UnsupportedClassError:
                        # known unsupported case
                        continue
                    except Exception as e:
                        # grace fully logged and ignored
                        logger.error(str(e))

        # combine results and refresh internal book-keeping
        self._devices = active_devices + inactive_devices

        return tuple(self._devices)

    @abstractmethod
    def _enumerate_device_candidates(self) -> Iterable[Device]:
        """
        Enumerate possible devices, but _not_ tested for compatibility.

        Note:
            Returned devices are _not_ tested nor active.
        """

    @classmethod
    def enumerate_supported_device_types(cls) -> Iterable[DeviceType]:
        """List device types that this driver may support."""
        hints = get_type_hints(cls._enumerate_device_candidates)["return"]
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
