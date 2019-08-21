from abc import ABCMeta, abstractmethod
import logging

all = ["Device", "DeviceManager"]

logger = logging.getLogger(__name__)


class Device(metaclass=ABCMeta):
    """
    Base class for all device type.
    """
    
    @classmethod
    @abstractmethod
    def discover(cls):
        """List supported hardwares."""
        raise NotImplementedError

    @abstractmethod
    def initialize(self):
        raise NotImplementedError

    @abstractmethod
    def close(self):
        raise NotImplementedError
