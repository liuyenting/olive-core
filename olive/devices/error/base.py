__all__ = ["UnsupportedDeviceError"]


class DeviceError(Exception):
    """Generic device error."""


class UnsupportedDeviceError(DeviceError):
    """Devic of interest does not belong to this class."""
