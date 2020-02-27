import logging

import aiohttp

from .model import devices

__all__ = []

logger = logging.getLogger(__name__)


class APIHelper(object):
    def __init__(self):
        self._session = aiohttp.ClientSession()

    ##

    @property
    def session(self):
        return self._sesion

    ##

    async def do_devices_api_call(self, request: devices.DevicesRequest):
        async with self.session.get() as response:
            assert response.status == 200
            return await response.json()
