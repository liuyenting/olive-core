from abc import ABCMeta, abstractmethod
import logging

from olive.core.resources import DeviceManager

all = ["Device", "DeviceManager"]

logger = logging.getLogger(__name__)


class Device(object):
    """
    Base class for all device type.
    """

    manager = DeviceManager()

    def __init__(self):
        self.manager.add_device(self)

    def __init_subclass__(cls, category=None):
        """
        Args:
            cls (type): new driver class
            category (type): category of the new driver
        """
        if category:
            cls.manager.add_driver(category, cls)
        else:
            logger.debug('ignore category class "{}"'.format(cls))


class Camera(Device):
    def __init__(self):
        super().__init__()
        print("Camera init()")

    def __init_subclass__(cls):
        super().__init_subclass__(category=Camera)


class ConcreteCameraDriver(Camera):
    def __init__(self):
        super().__init__()
        print("ConcreteCamera init()")


if __name__ == "__main__":
    mgr = DeviceManager()

    def print_drivers():
        print("/// DRIVERS ///")
        for category, drivers in mgr.get_drivers().items():
            print(str(category))
            for driver in drivers:
                print(".. {}".format(str(driver)))

    def print_devices():
        print("/// DEVICES ///")
        for uuid, device in mgr.get_devices().items():
            print("{}, {}".format(uuid, device))
        print()

    print_drivers()
    print_devices()

    new_camera = ConcreteCameraDriver()

    print_drivers()
    print_devices()
