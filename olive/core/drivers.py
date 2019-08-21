import importlib
import inspect
import itertools
import logging
import pkgutil

from olive.core.utils import Singleton
import olive.devices
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

    def __init__(self, blacklist=[]):
        # populate categories
        self._drivers = {klass: [] for klass in Device.__subclasses__()}

        self.refresh()

        # TODO isolate list_drivers, use result from _active/_inactive, with category filter

    def refresh(self):
        """Refresh known driver list."""
        # TODO deactivate first

        for drivers in self._drivers.values():
            del drivers[:]

        for driver in self._enumerate_drivers():
            # determine category
            for parent in self._drivers.keys():
                if issubclass(driver, parent):
                    self._drivers[parent].append(driver)
                    break
            else:
                # this should _never_ happen
                logger.warning(
                    f'"{driver} inherit from an unknown device type, ignored'
                )
                continue

    def query_devices(self, category):
        pass

    @property
    def drivers(self):
        return list(itertools.chain.from_iterable(self._drivers.values()))

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

    def _enumerate_drivers(self):
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

    def _find_parent(self, klass):
        pass


if __name__ == "__main__":
    import coloredlogs

    coloredlogs.install(
        level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
    )

    dm = DriverManager()

    from pprint import pprint

    pprint(dm.drivers)
    pprint(dm._drivers)

    from olive.devices.modulator import AcustoOpticalModulator

    aom = AcustoOpticalModulator()