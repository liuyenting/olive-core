from abc import abstractmethod
import logging
from typing import get_type_hints

from olive.devices.base import Device

__all__ = ["DriverType", "Driver"]

logger = logging.getLogger(__name__)


class DriverType(type):
    """All drivers belong to this type."""


class Driver(metaclass=DriverType):
    @abstractmethod
    def __init__(self):
        """Abstract __init__ to prevent instantiation."""

    """
    Driver initialization.
    """

    @abstractmethod
    def initialize(self):
        """Initialize the library. Most notably for singleton instance."""

    @abstractmethod
    def shutdown(self):
        """Cleanup resources allocated by the library."""

    @abstractmethod
    async def enumerate_devices(self) -> None:
        """List devices that this driver can interact with."""

    @classmethod
    def enumerate_supported_device_types(cls):
        """List device types that this driver may support."""
        hints = get_type_hints(cls.enumerate_devices)["return"]
        try:
            klasses = hints.__args__
        except AttributeError:
            # not a union
            klasses = [hints]

        # remap to device primitives
        devices = []
        for klass in klasses:
            devices.extend(klass.__bases__)
        return tuple(set(devices) & set(Device.__subclasses__()))
