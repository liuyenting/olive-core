import logging

from requests import Session

from .host import Host

__all__ = []

logger = logging.getLogger(__name__)


class APIHelper(object):
    def __init__(self, url_root: str):
        self._session = Session()

        logger.info(f'establishing connection with "{url_root}"')

        # establish endpoints
        self.host = Host(url_root, self._session)

    ##

    ##

    def close(self):
        """Close the API helper."""
        self._session.close()
