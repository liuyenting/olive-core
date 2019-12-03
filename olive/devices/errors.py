class DeviceError(Exception):
    """Base class."""


class OutOfRangeError(DeviceError, ValueError):
    """Parameter out-of-range."""


class UnknownCommandError(DeviceError, SyntaxError):
    """Unknown command."""


class UnsupportedDeviceError(DeviceError):
    """Device not supported by current driver."""


##


class CameraError(DeviceError):
    """Error base class for camera devices."""


##


class LightSourceError(DeviceError):
    """Error base class for light source devices."""


##


class ModulatorError(DeviceError):
    """Error base class for modulator devices."""


##


class MotionError(DeviceError):
    """Error base class for motion devices."""


##


class SensorError(DeviceError):
    """Error base class for sensor devices."""
