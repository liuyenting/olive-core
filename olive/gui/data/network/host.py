import logging

from requests.compat import urljoin

from .base import APIClient

__all__ = ["Host"]

logger = logging.getLogger(__name__)


class Host(APIClient):
    def hostname(self) -> str:
        path = urljoin(self.root, "/host/hostname")
        print(path)
        response = self.session.get(path)
        assert response.status_code == 200
        return response.text
