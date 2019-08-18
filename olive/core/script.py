from abc import ABCmeta, abstractmethod
import logging

logger = logging.getLogger(__name__)


class Script(metaclass=ABCmeta):
    """
    Define how the system behave per acquisition request.
    """

    def __init__(self):
        pass

    @abstractmethod
    def eval(self):
        pass
