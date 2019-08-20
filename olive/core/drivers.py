import importlib
import inspect
import logging
import pkgutil

from olive.core.utils import Singleton
from olive.devices.base import Device

import olive.drivers

__all__ = ["DriverManager"]

logger = logging.getLogger(__name__)


class DriverManager(metaclass=Singleton):
    """
    Driver bookkeeping.

    Todo:
        - blacklist
        - driver reload
    """

    def __init__(self):
        # first run refresh
        self._active = []
        self._inactive = self.list_drivers()

        # TODO refresh
        # TODO organize drivers

        # TODO isolate list_drivers, use result from _active/_inactive, with category filter

    def list_drivers(self, category=None):
        """
        Iterate over the driver namespace and list out all potential drivers.

        Args:
            category (Device): device type class

        Returns:
            (list): a list of drivers
        """
        drv = []
        drv_pkgs = DriverManager._iter_namespace(olive.drivers)
        for _, name, is_pkg in drv_pkgs:
            drv_pkg = importlib.import_module(name)
            _drv = []
            for _, klass in inspect.getmembers(drv_pkg, inspect.isclass):
                if issubclass(klass, Device):
                    _drv.append(klass)
            logger.debug(f'"{name}" contains {len(_drv)} driver(s)')
            for klass in _drv:
                logger.debug(f".. {klass.__name__}")
            drv.extend(_drv)
        logger.info(f"{len(drv)} driver(s) loaded")
        return drv

    def query_devices(self, category):
        pass

    @property
    def active_drivers(self):
        return self._active

    @property
    def drivers(self):
        return self.active_drivers + self.inactive_drivers

    @property
    def inactive_drivers(self):
        return self._inactive

    @staticmethod
    def _iter_namespace(pkg_name):
        """
        Iterate over a namespace package.

        Args:
            pkg_name (type): namespace package to iterate over

        Returns:
            (tuple): tuple containing
                finder (FileFinder): module location
                name (str): fully qualified name of the found item
                is_pkg (bool): whether the found path is a package
        """
        return pkgutil.iter_modules(pkg_name.__path__, pkg_name.__name__ + ".")


if __name__ == "__main__":
    import coloredlogs

    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    dm = DriverManager()
