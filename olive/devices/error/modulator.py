from .base import DeviceError


class ModulatorError(DeviceError):
    """Generic modulator error."""


class ChannelExistsError(ModulatorError):
    """Assigned alias already defined."""


class ExceedsChannelCapacityError(ModulatorError):
    """Reached maximum number of channels."""
