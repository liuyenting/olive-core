import logging


import qdarkstyle
from qtpy.QtWidgets import QApplication

from olive.ui.app import Controller as _Controller

__all__ = ["Controller"]

logger = logging.getLogger(__name__)


class Controller(_Controller):
    """
    App controller manages the background service and presenter/view instantiation.
    """

    def __init__(self):
        super().__init__()

        app = QApplication
        app.setStyleSheet(qdarkstyle.load_stylesheet())

        self._app = app

    ##

    @property
    def app(self) -> QApplication:
        return self._app

    ##

    def run(self):
        # create main window
        pass

        # launch
