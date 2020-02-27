import logging

from aiohttp.web import Application, run_app

from .routes import devices
from .gateway import Gateway

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
        app = Application()

        # attach API endpoints
        # NOTE by adding subapp, we can introduce API versioning in the future
        app.add_subapp("/api", self.api)

        run_app(app, host=self._host, port=self._port)


def launch(port=None):
    controller = AppController(port=port)
    controller.run()
