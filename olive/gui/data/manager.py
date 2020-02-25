import logging

from olive.utils import Singleton

__all__ = ["DataManager"]

logger = logging.getLogger(__name__)


class DataManager(metaclass=Singleton):
    pass
