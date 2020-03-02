import asyncio
import logging
from multiprocessing import Event
from typing import Optional

from aiohttp.web import Application, AppRunner, TCPSite

from .gateway import Gateway
from .routes import devices, host
from .utils import find_free_port

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class EventInterrupt(Exception):
    """Raised when the interrupt event is triggered."""


async def wakeup(event: Optional[Event] = None):
    """
    Work around for Windows signal handlers.

    Args:
        event (Event, optional): using external event to generate interrupt

    References:
        - asyncio: support signal handlers on Windows (feature request)
            https://bugs.python.org/issue23057
        - Why does the asyncio's event loop suppress the KeyboardInterrupt on
            Windows?
            https://stackoverflow.com/a/36925722
    """
    while True:
        if event and event.is_set():
            # trigger termination
            raise EventInterrupt()
        await asyncio.sleep(1)


class AppController(object):
    """
    Args:
        host (str, optional): local binding address
        port (int, optional): port to listen
        version (int, optional): API version
    """

    def __init__(
        self,
        host: Optional[str] = "localhost",
        port: Optional[int] = None,
        version: Optional[int] = 1,
    ):
        self._host = host
        self._port = find_free_port() if port is None else port

        self._api = Application()
        self._version = version

        self.setup_routes()
        self.setup_gateway()

    ##

    @property
    def api(self) -> Application:
        """API endpoints."""
        return self._api

    @property
    def url(self) -> str:
        return f"http://{self._host}:{self._port}/v{self._version}"

    ##

    def setup_routes(self):
        """Setup routing tables."""
        # /host
        self.api.router.add_routes(host.routes)
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

    def run(self, event: Optional[Event] = None):
        """
        Kick start the OLIVE service.

        Args:
            event (Event, optional): using external event to generate interrupt
        """
        loop = asyncio.get_event_loop()

        app = Application()

        # attach API endpoints
        # NOTE by adding subapp, we can introduce API versioning in the future
        app.add_subapp(f"/v{self._version}", self.api)

        # create runner
        runner = AppRunner(app)
        loop.run_until_complete(runner.setup())
        # create the site
        logger.info(f"OLIVE service is now listen on {self._host}:{self._port}")
        site = TCPSite(runner, host=self._host, port=self._port)

        # run!
        try:
            loop.run_until_complete(asyncio.gather(*[site.start(), wakeup(event)]))
        except KeyboardInterrupt:
            logger.info("keyboard interrupted")
        except EventInterrupt:
            logger.debug("event interrupt")
        finally:
            loop.run_until_complete(runner.cleanup())


def launch(**kwargs):
    """Alias to start the OLIVE service."""
    controller = AppController(**kwargs)
    controller.run()
