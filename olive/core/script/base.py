from abc import ABCmeta, abstractmethod
import logging


__all__ = ["Script"]

logger = logging.getLogger(__name__)


class Script(metaclass=ABCmeta):
    """
    Define how the system behave per acquisition request.
    """

    #: device name in the script and their managed ID
    _device_alias = {}

    def __init__(self):
        pass

    @abstractmethod
    def setup(self):
        raise NotImplementedError

    @abstractmethod
    def loop(self):
        raise NotImplementedError

    def eval(self):
        """
        TODO
            1) convert all annotated properties to _device_alias

                main_camera = 
        """
        pass
