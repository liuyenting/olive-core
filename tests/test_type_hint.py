from abc import ABC, ABCMeta, abstractmethod
from typing import get_type_hints


class DriverType(type):
    """New type for drivers."""


class Driver(type, metaclass=DriverType):
    """
    Driver initialization.
    """

    def initialize(self):
        pass

    def shutdown(self):
        pass

    """
    Device initialization.
    """

    def open(self):
        """Open device session."""

    def close(self):
        """Close device session."""


class DeviceType(type):
    def __new__(cls, name, bases, dct):
        print(name)
        return super().__new__(cls, name, bases, dct)


class Device(metaclass=DeviceType):
    def __init__(self):
        super().__init__()
        print("Device.__init__")


class PDeviceA(Device):
    def __init__(self):
        super().__init__()
        print("PDeviceA.__init__")


class PDeviceB(Device):
    def __init__(self):
        super().__init__()
        print("PDeviceB.__init__")


class PDeviceAA(PDeviceA, Device):
    def __init__(self):
        super().__init__()
        print("PDeviceAA.__init__")


###


class DeviceA(PDeviceAA):
    def __init__(self):
        super().__init__()
        print("DeviceA.__init__")


class DeviceB(PDeviceB):
    def __init__(self):
        super().__init__()
        print("DeviceB.__init__")


##


class DriverA(Driver):
    def __init__(self):
        pass

    """
    def open(self) -> DeviceA:
        pass
    """


device = DeviceA()

print(type(DriverA))
print(get_type_hints(DriverA.open))

print(type(DeviceA))
print(type(PDeviceAA))
print(type(PDeviceA))
print(type(DeviceType))

print("\n** type(device), subclass **")
klass = type(device)
print(issubclass(klass, PDeviceA))
print(issubclass(klass, PDeviceB))
print(issubclass(klass, PDeviceAA))
print(issubclass(klass, DeviceA))
print(issubclass(klass, DeviceB))

print("\n** subclass(*, Device) **")
print(issubclass(PDeviceA, Device))
print(issubclass(PDeviceB, Device))
print(issubclass(PDeviceAA, Device))
print(issubclass(DeviceA, Device))
print(issubclass(DeviceB, Device))

print('\n** Device.__subclasses__ **')
print(Device.__subclasses__())