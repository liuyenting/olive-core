import asyncio
import logging

from aiohttp.web import Application, AppRunner, TCPSite, run_app

from .gateway import Gateway
from .routes import devices

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    def __init__(self, host=None, port=None):
        self._host, self._port = host, port

        self._api = Application()

        self.setup_routes()
        self.setup_gateway()

    ##

    @property
    def api(self) -> Application:
        """API endpoints."""
        return self._api

    ##

    def setup_routes(self):
        """Setup routing tables."""
        # /devices
        # /devices/{uuid}
        # /devices/categories
        self.api.router.add_routes(devices.routes)

    def setup_gateway(self):
        gateway = Gateway()
        self.api.on_startup.append(gateway.initialize)
        self.api.on_cleanup.append(gateway.shutdown)

        # save it in context
        self.api["gateway"] = gateway

    ##

    def run(self):
        loop = asyncio.get_event_loop()

        app = Application()

        # attach API endpoints
        # NOTE by adding subapp, we can introduce API versioning in the future
        app.add_subapp("/api", self.api)

        # create runner
        runner = AppRunner(app)
        loop.run_until_complete(runner.setup())
        # create the site
        site = TCPSite(runner, host=self._host, port=self._port)

        # work around for Windows signal handlers
        # NOTE https://bugs.python.org/issue23057
        async def wakeup():
            while True:
                await asyncio.sleep(1)

        # run!
        try:
            loop.run_until_complete(asyncio.gather(*[site.start(), wakeup()]))
        except KeyboardInterrupt:
            logger.info("keyboard interrupted, stopping")
            loop.run_until_complete(runner.cleanup())


def launch(port=None):
    controller = AppController(port=port)
    controller.run()
