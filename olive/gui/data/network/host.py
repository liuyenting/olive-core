import logging

from .base import APIClient

__all__ = ["Host"]

logger = logging.getLogger(__name__)


class Host(APIClient):
    def hostname(self) -> str:
        response = self.get("/host/hostname")
        assert response.status_code == 200
        return response.text
