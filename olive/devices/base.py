from abc import ABCMeta, abstractmethod
import logging

all = ["Device"]

logger = logging.getLogger(__name__)


class Device(metaclass=ABCMeta):
    """
    Base class for all device type.
    """

    @abstractmethod
    def __init__(self):
        """
        Note:
            Prevent user from instantiation.
        """
        pass

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

    @abstractmethod
    def get_attribute(self, name):
        """
        Get the value of device attributes.

        Args:
            name (str): documented attribute name
        """
        raise NotImplementedError

    @abstractmethod
    def set_attribute(self, name, value):
        """
        Set the value of device attributes.

        Args:
            name (str): documented attribute name
            value : new value of the specified attribute
        """
        raise NotImplementedError
