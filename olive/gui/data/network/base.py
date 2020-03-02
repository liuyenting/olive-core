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
        # ensure the root does not have trailing slash
        if url_root[-1] == "/":
            url_root = url_root[:-1]

        self._url_root = url_root
        self._session = session

    ##

    # TODO websocket


def bind_method(method):
    """
    Bind HTTP verbs to the APIclient class.

    Reference:
        Hammock
            https://github.com/kadirpekel/hammock
    """

    def func(self, path, **kwargs):
        # generate absolute path
        # NOTE requests.compat.urljoin requires common denominator to work, in this
        #   case, we do not have this
        url = self._url_root + path
        print(f"bind_method.func, {url}")
        return self._session.request(method, url, **kwargs)

    return func


# patch APIClient with HTTP verbs
for method in (
    "delete",
    "get",
    "post",
    "put",
):
    setattr(APIClient, method, bind_method(method))
