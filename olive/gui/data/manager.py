import logging

from olive.utils import Singleton

from .network import APIHelper

__all__ = ["DataManager"]

logger = logging.getLogger(__name__)


class DataManager(metaclass=Singleton):
    def __init__(self):
        self._api = None

    ##

    @property
    def api(self) -> APIHelper:
        assert self._api is not None, "API not initiated"
        return self._api

    ##

    def set_service_url(self, url_root):
        """Set service URL in order to open interface to the API."""
        if self._api is not None:
            logger.info(f"found previous connection, closing")
            # we have to close it first
            self._api.close()

        self._api = APIHelper(url_root)
