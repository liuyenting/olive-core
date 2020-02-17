from .base import ManagerException


class DeviceManagerException(ManagerException):
    """Generic device manager exception."""


class DeviceTimeoutException(DeviceManagerException):
    """Timeout occurs during (un)registration."""
