import logging
import sys

import qdarkstyle
from qtpy.QtWidgets import QApplication

from .mainwindow import MainWindow

__all__ = []

logger = logging.getLogger(__name__)


def launch():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
