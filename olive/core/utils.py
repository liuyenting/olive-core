from functools import wraps
import importlib
import inspect
import logging
import pkgutil
import time

__all__ = ["enumerate_namespace_subclass", "retry", "Singleton"]

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            logger.debug('new singleton object "{}" created'.format(cls))
        return cls._instances[cls]


def retry(exception, n_trials=3, delay=1, backoff=2, logger=None):
    """
    Retry calling the decorated function using an exponential backoff.

    Args:
        exception (Exception or tuple): the exception(s) to check
        n_trials (int): number of trials
        delay (int): initial delay between retries in seconds
        backoff (int): backoff multiplier
        logger (Logger): logging module to use
    """

    def retry_func(func):
        """Create a retry decorator according to requirement."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            """The wrapped function."""
            remain, next_delay = n_trials, delay
            while remain > 1:
                try:
                    return func(*args, **kwargs)
                except exception:
                    if logger:
                        logger.warning(f"retry in {next_delay} seconds...")
                    time.sleep(next_delay)
                    next_delay *= backoff
                remain -= 1
            # last run
            return func(*args, **kwargs)

        return wrapped

    return retry_func


def iter_namespace(pkg_name):
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


def enumerate_namespace_subclass(pkg, base):
    """
    Iterate over namespace and list all subclasses.

    Args:
        pkg (package): namespace package of intereset
        base (class): base class

    Returns:
        (list): list of subclass of base
    """
    klasses = []
    pkgs = iter_namespace(pkg)
    for _, name, is_pkg in pkgs:
        pkg = importlib.import_module(name)
        _klasses = []
        for _, klass in inspect.getmembers(pkg, inspect.isclass):
            if issubclass(klass, base):
                _klasses.append(klass)
        logger.debug(f'"{name}" contains {len(_klasses)} subclass(es)')
        for klass in _klasses:
            logger.debug(f".. {klass.__name__}")
        klasses.extend(_klasses)
    logger.info(f"{len(klasses)} subclass(es) of {base.__name__} loaded")
    return klasses
