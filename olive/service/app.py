import logging

from aiohttp.web import Application, run_app

from .routes import devices

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    def __init__(self, host=None, port=None):
        self._host, self._port = host, port

        # create api root application
        api = Application()

        # install routes
        api.router.add_routes(devices.routes)

        # create actual root
        app = Application()
        app.add_subapp("/api/", api)
        self._app = app

    def run(self):
        run_app(self._app, host=self._host, port=self._port)


def launch(port=None):
    controller = AppController(port=port)
    controller.run()
