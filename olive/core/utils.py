from functools import wraps
import logging
import time

__all__ = ["retry", "Singleton"]

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
