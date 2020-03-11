class DeviceError(Exception):
    """Generic device error."""


##
# initialization


class UnsupportedClassError(DeviceError):
    """Device does not belong to this class."""


class DeviceTimeoutError(DeviceError):
    """Response timeout."""


##
# cache


class CacheError(DeviceError):
    """Generic cache error."""


class DirtyPropertyCacheError(CacheError):
    """Dirty property cache error."""
