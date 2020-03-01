import logging
import os

from requests import Session

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

    def __init__(self, url_root: str, session: Session):
        self.root = url_root
        self.session = session

    ##

    # TODO websocket

