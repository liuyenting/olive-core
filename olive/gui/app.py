import logging
import sys

from qtpy.QtWidgets import QApplication
import qdarkstyle

from .data import DataManager
from .main import MainView, MainPresenter

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet())
        self._app = app

    def run(self, url):
        data = DataManager()
        data.set_service_url(url)

        # kick start main window
        view = MainView()
        presenter = MainPresenter(view)  # noqa, keep the reference

        # show the start view
        view.show()

        # start event loop
        self._app.exec_()


def launch():
    # TODO test for service endpoint availability
    from multiprocessing import Process
    from olive.service import app

    host = "localhost"
    port = 7777
    api_version = 1
    url = "http://{}:{}/v{}".format(host, port, api_version)
    logger.debug(f'launching service at "{url}"')

    # launch local service
    service = Process(target=app.launch, args=(port,))
    service.start()

    controller = AppController()
    controller.run(url)  # establish local connection
    # TODO why the fuck URL is not working?

    # clean up the service
    logger.info("joining local service process")
    service.join()  # TODO send keyboard interrupt
