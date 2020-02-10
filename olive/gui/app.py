import logging
import sys

import qdarkstyle
from qtpy.QtWidgets import QApplication, QMainWindow

from .main_window import Ui_MainWindow

__all__ = []

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


def launch():
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())
