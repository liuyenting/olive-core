import logging
import sys

from qtpy.QtWidgets import QApplication
import qdarkstyle

from olive.utils import Singleton

from .mainwindow import MainWindowPresenter

__all__ = ["Controller"]

logger = logging.getLogger(__name__)


class Controller(metaclass=Singleton):
    """
    App controller manages the background service and presenter/view instantiation.

    Args:
        backend (str): name of the backend to use
    """

    def __init__(self):
        print('controller init')

    ##

    ##

    def run(self):
        """
        Primary entry point for the application.
            1) Start background acquisition service.
            2) Create user interface.
        """

        app = QApplication()
        app.setStyleSheet(qdarkstyle.load_stylesheet())

        # TODO kick start background service

        main_window = MainWindowPresenter()

        # TODO link main window with model/interactor

        self.views.run_event_loop()

        # TODO cleanup

        app.exec_()
