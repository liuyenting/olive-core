import logging
import sys

from qtpy.QtWidgets import QApplication
import qdarkstyle

from .main import MainView, MainPresenter

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    def __init__(self):
        app = QApplication(sys.argv)
        app.setStyleSheet(qdarkstyle.load_stylesheet())
        self._app = app

    def run(self):
        # kick start main window
        view = MainView()
        presenter = MainPresenter(view)

        view.show()

        self._app.exec_()


def launch():
    controller = AppController()
    controller.run()
