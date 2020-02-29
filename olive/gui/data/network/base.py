import logging
import os

from aiohttp import ClientSession

__all__ = ["APIClient"]

logger = logging.getLogger(__name__)


class APIClient(object):
    """
    This class provides the basis for interacting with the srevice API. Client session
    and root URI are all wrapped in this class, so inherited client can focus their
    effort on wrapping the REST API.

    All the arguments and responses are expected to be a JSON object. Therefore, no
    query string used in the URL (query strings cannot describe complex structure and
    have length limitation).

    Args:
        uri_root (str): URI of the service
        session (ClientSession): connection pool
    """

    def __init__(self, uri_root: str, session: ClientSession):
        self._root = uri_root
        self._session = session

    ##

    async def get(self, path):
        uri = os.path.join(self._root, path)
        async with self._session.get(uri) as response:
            return response.status, response.json()

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    ##

    # TODO websocket
