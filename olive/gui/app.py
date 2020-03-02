import logging
import sys
from multiprocessing import Event, Process
from typing import Optional

import qdarkstyle
from qtpy.QtWidgets import QApplication

from .data import DataManager
from .main import MainPresenter, MainView
from .utils import is_port_binded

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    """
    Args:
        host (str, optional): service host address
        port (int, optional): service port
        version (int, optional): API version
    """

    def __init__(
        self,
        host: Optional[str] = "localhost",
        port: Optional[int] = None,
        version: Optional[int] = 1,
    ):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet())
        self._app = app

        self._host, self._port = host, port
        self._version = version

        self._service, self._event = None, None

    ##

    def run(self):
        """
        Run OLIVE.

        Note:
            If OLIVE service is not running, we will try to start it as well.
        """
        data = DataManager()

        # try to connect to the service using waht we have
        url = None
        if self._host == "localhost":
            if self._port and is_port_binded("localhost", self._port):
                logger.info(f"local OLIVE service is running")
            else:
                url = self.run_service()

        if url is None:
            # build url string using updated info
            url = "http://{}:{}/v{}".format(self._host, self._port, self._version)

        # update the URL root
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

    def run_service(self):
        """
        Run the OLIVE service.

        Returns:
            url (str): the URL that points to OLIVE service
        """
        try:
            from olive.service import app
        except ImportError:
            logger.error("OLIVE service not installed")
            raise

        # create service controller
        controller = app.AppController(port=self._port, version=self._version)
        url = controller.url

        # run the service in another process
        event = Event()
        service = Process(target=controller.run, args=(event,))
        service.start()

        self._service, self._event = service, event

        return url


def launch(**kwargs):
    """Alias to start the user interface."""
    controller = AppController(**kwargs)
    controller.run()
