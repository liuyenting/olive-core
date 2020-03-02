import asyncio
import logging
import signal
from multiprocessing import Event
from typing import Optional

from aiohttp.web import Application, AppRunner, TCPSite

from .gateway import Gateway
from .routes import devices, host

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

    def run(self, event: Optional[Event]):
        """
        Kick start the OLIVE service.

        Args:
            event (Event, optional): using external event to generate interrupt
        """
        loop = asyncio.get_event_loop()

        app = Application()

        # attach API endpoints
        # NOTE by adding subapp, we can introduce API versioning in the future
        app.add_subapp("/v1", self.api)

        # create runner
        runner = AppRunner(app)
        loop.run_until_complete(runner.setup())
        # create the site
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


def launch(port=None, event=None):
    controller = AppController(port=port)
    controller.run(event)
