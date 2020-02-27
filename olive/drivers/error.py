class DriverError(Exception):
    """Generic driver error."""


class InitializeError(DriverError):
    """Failed to initialize the driver."""


class ShutdownError(DriverError):
    """Failed to shutdown the driver."""


##


class SerialPortManagerError(DriverError):
    """Generic serial port manager error."""


class PortAlreadyAssigned(SerialPortManagerError):
    """Selected port already found its driver and assigned."""
