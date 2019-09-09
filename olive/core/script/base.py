from abc import ABCMeta, abstractmethod
import logging

from olive.core import DeviceType

__all__ = ["Script"]

logger = logging.getLogger(__name__)


class Script(metaclass=ABCMeta):
    """
    Define how the system behave per acquisition request.
    """

    #: device name in the script and their managed ID
    _device_alias = {}

    def __init__(self):
        pass

    ##

    def get_requirements(self):
        """Retreieve device requirement of the script."""
        # only test non-inherited attributes
        attrs = set(dir(self)) - set(dir(Script))
        attrs = [getattr(self, attr) for attr in attrs]
        # ... we only cares about Device
        return [attr for attr in attrs if issubclass(type(attr), DeviceType)]

    def evaluate(self):
        """
        TODO
            1) convert all annotated properties to _device_alias

                main_camera =
        """
        pass

    ##

    @abstractmethod
    def setup(self):
        raise NotImplementedError

    @abstractmethod
    def loop(self):
        raise NotImplementedError

