from abc import ABCMeta, abstractmethod
import logging

from olive.core.devices import DeviceManager

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


if __name__ == "__main__":
    import coloredlogs
    from pprint import pprint

    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    # prime the drivers
    from olive.core.drivers import DriverManager

    drv_mgr = DriverManager()

    pprint([cls.__name__ for cls in Device.__subclasses__()])
