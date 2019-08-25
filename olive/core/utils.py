import logging

__all__ = ["Singleton"]

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            logger.debug('new singleton object "{}" created'.format(cls))
        return cls._instances[cls]
