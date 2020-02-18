class DeviceError(Exception):
    """Generic device error."""


class UnsupportedClassError(DeviceError):
    """Device does not belong to this class."""


class DeviceTimeoutError(DeviceError):
    """Response timeout."""
