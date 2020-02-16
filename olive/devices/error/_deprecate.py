from .base import DeviceError


class OutOfRangeError(DeviceError, ValueError):
    pass


class UnknownCommandError(DeviceError, SyntaxError):
    pass
