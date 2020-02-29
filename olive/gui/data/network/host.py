import logging

from .base import APIClient

__all__ = ["Host"]

logger = logging.getLogger(__name__)


class Host(APIClient):
    def __init__(self, *args):
        super().__init__(*args)

    ##

    async def hostname(self) -> str:
        await self.get("/host")
        async with self.get("/host") as response:
            assert response.status == 200
            return await response.json()
        return self._session

    ##

    async def all_info(self):
        async with self.get("/host") as response:
            assert response.status == 200
            return

