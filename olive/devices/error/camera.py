from .base import DeviceError


class CameraError(DeviceError):
    """Generic camera error."""


class FrameBufferError(CameraError):
    """Generic frame buffer error."""


class HostOutOfMemoryError(FrameBufferError):
    """Host does not have enough memory for the frame buffer."""


class NotEnoughBufferError(FrameBufferError):
    """Frame buffer does not have enough clean frames."""
