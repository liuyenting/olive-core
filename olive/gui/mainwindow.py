import logging
import os

import coloredlogs

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QDesktopWidget,
    QDockWidget,
    QMainWindow,
    QToolBar,
    QStatusBar,
)

from olive.gui.resources import ICON

__all__ = ["MainWindow"]

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

logger = logging.getLogger(__name__)


class StatusBarLogger(logging.Handler):
    def __init__(self, statusbar: QStatusBar, timeout=5000):
        super().__init__()
        self.statusbar = statusbar
        self.timeout = timeout

    def emit(self, record):
        message = self.format(record)
        self.statusbar.showMessage(message, self.timeout)

    def writes(self, message):
        pass


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Olive")

        # DEBUG, (800, 600)
        self.init_window_size((1024, 768))

        self.setup_menubar()
        self.setup_toolbar()
        self.setup_dockwidgets()
        self.setup_statusbar()

        logger.info("Done")

    ##

    def init_window_size(self, size=None, ratio=0.7):
        """
        Initial window size. If not specified, default to 70% of the screen size.
        """
        if size is None:
            size = QDesktopWidget().availableGeometry().size() * ratio
        elif isinstance(size, tuple):
            size = QSize(*size)
        self.resize(size)

    ##

    def setup_menubar(self):
        menubar = self.menuBar()

        """
        File
        """
        file_menu = menubar.addMenu("File")
        file_menu.addAction('New Profile')
        file_menu.addSeparator()
        file_menu.addAction("Quit")

        """
        Tools
        """
        tools_menu = menubar.addMenu("Tools")

        """
        Views
        """
        views_menu = menubar.addMenu("Views")
        views_menu.addAction("Script Debugger Toolbar")
        views_menu.addAction("Parameters Toolbar")
        views_menu.addAction("Acquisition Toolbar")
        views_menu.addSeparator()
        views_menu.addAction("Mono View")
        views_menu.addAction("Dual View")
        views_menu.addAction("Quad View")

        """
        Help
        """
        help_menu = menubar.addMenu("Help")
        help_menu.addAction("About")

    def setup_toolbar(self):
        pass

    def setup_dockwidgets(self):
        # TODO populate dockwidgets using supported script features
        # NOTE who to query the features? dispatcher?
        pass

    def setup_statusbar(self):
        handler = StatusBarLogger(self.statusBar())
        logging.getLogger().addHandler(handler)


if __name__ == "__main__":
    from PySide2.QtWidgets import QApplication

    app = QApplication()
    mw = MainWindow()
    mw.show()
    app.exec_()
