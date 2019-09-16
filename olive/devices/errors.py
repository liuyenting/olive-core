class DeviceError(Exception):
    """Base class."""


class UnsupportedDeviceError(DeviceError):
    """Device not supported by current driver."""
