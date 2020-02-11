import logging
import sys

import qdarkstyle
from qtpy.QtWidgets import QApplication

from olive.gui.backend.qt import mainwindow

__all__ = []

logger = logging.getLogger(__name__)


def launch():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    v = mainwindow.MainWindowView()
    p = mainwindow.MainWindowPresenter(v)

    sys.exit(app.exec_())
