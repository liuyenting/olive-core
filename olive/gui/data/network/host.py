import logging
import os

from .base import APIClient

__all__ = ["Host"]

logger = logging.getLogger(__name__)


class Host(APIClient):
    def hostname(self) -> str:
        path = os.path.join(self.root, "/host/hostname")
        response = self.session.get(path)
        assert response.status_code == 200
        return response.text
