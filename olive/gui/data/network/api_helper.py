import logging

from requests import Session

from .host import Host
from .model import devices

__all__ = []

logger = logging.getLogger(__name__)


class APIHelper(object):
    def __init__(self, url_root: str):
        self._session = Session()

        # establish endpoints
        self.host = Host(url_root, self._session)
