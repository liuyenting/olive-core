import logging
import sys
from multiprocessing import Event, Process
from typing import Optional

import qdarkstyle
from qtpy.QtWidgets import QApplication

from olive.service import app

from .data import DataManager
from .main import MainPresenter, MainView
from .utils import is_port_binded, find_free_port

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet())
        self._app = app

        self._service, self._event = None, None

    ##

    def run(self, host=None, port=None, version=1):
        """
        Run OLIVE.

        Args:
            host (str, optional): host address
            port (int, optional): target port
            version (int, optional): API version

        Note:
            If OLIVE service is not running, we will try to start it as well.
        """
        if host is None:
            host = "localhost"
            # we should connect to a local service
            if port and is_port_binded("localhost", port):
                logger.info(f"local OLIVE service is running")
            else:
                port = self.run_service(port)
        # generat url
        url = "http://{}:{}/v{}".format(host, port, version)

        data = DataManager()
        data.set_service_url(url)

        # kick start main window
        view = MainView()
        presenter = MainPresenter(view)  # noqa, keep the reference

        # show the start view
        view.show()

        # start event loop
        self._app.exec_()

        # if we have the service reference, we started it, therefore, we have to stop it
        if self._service is not None:
            logger.info("terminating local service process")
            self._event.set()
            # waiting for it to actually close
            self._service.join()
            self._service.close()

    def run_service(self, port=None):
        """
        Run the OLIVE service.

        Args:
            port (int, optional): port OLIVE service will listen to

        Returns:
            port (int): the port OLIVE is listening to
        """
        port = find_free_port() if port is None else port
        logger.info(f"launching local service at port {port}")

        event = Event()
        service = Process(target=app.launch, args=(port, event))
        service.start()

        self._service, self._event = service, event

        return port


def launch():
    controller = AppController()
    controller.run()
    # TODO why the fuck URL is not working?
