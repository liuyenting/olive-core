class DriverError(Exception):
    """Generic driver error."""


class InitializeError(DriverError):
    """Failed to initialize the driver."""


class ShutdownError(DriverError):
    """Failed to shutdown the driver."""
