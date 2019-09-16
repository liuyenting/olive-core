import logging
import os

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QDesktopWidget, QDockWidget, QMainWindow, QToolBar

from olive.gui.resources import ICON

__all__ = ["MainWindow"]

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Olive")

        # DEBUG, (800, 600)
        self.init_window_size((800, 600))

        self.create_acq_profile_toolbar()

        self.center()
        self.create_z_window()
        self.create_temporal_window()

    def init_window_size(self, size=None, ratio=0.7):
        """
        Initial window size. If not specified, default to 70% of the screen size.
        """
        if size is None:
            size = QDesktopWidget().availableSubitemGeometry().size() * ratio
        elif isinstance(size, tuple):
            size = QSize(*size)
        self.resize(size)

    def create_acq_profile_toolbar(self):
        toolbar = QToolBar("Profile")
        toolbar.actionTriggered.connect(self.debug)

        action = toolbar.addAction(ICON("XY.png"), "XY")
        action.setCheckable(True)

        action = toolbar.addAction(ICON("Z.png"), "Z")
        action.setCheckable(True)

        action = toolbar.addAction(ICON("C.png"), "Excitation")
        action.setCheckable(True)

        action = toolbar.addAction(ICON("T.png"), "Temporal")
        action.setCheckable(True)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def debug(self, action):
        status = "show" if action.isChecked() else "hide"

        logger.debug(f"{action.text()} {status}")

    def center(self):
        win = QDockWidget("Viewer")
        self.setCentralWidget(win)

    def create_temporal_window(self):
        win = QDockWidget("Temporal")
        win.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.addDockWidget(Qt.LeftDockWidgetArea, win)

    def create_z_window(self):
        win = QDockWidget("Z")
        win.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        # TODO return toggleViewAction -> toolbar
        self.addDockWidget(Qt.LeftDockWidgetArea, win)
