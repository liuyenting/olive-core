from .base import DeviceError


class CameraError(DeviceError):
    """Generic camera error."""


class HostOutOfMemoryError(DeviceError):
    """Host does not have enough memory for the frame buffer."""
