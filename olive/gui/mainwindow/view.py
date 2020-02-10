import logging
import os

from qtpy.QtWidgets import QMainWindow

from ..utils import load_ui_file

__all__ = ["MainWindow"]

logger = logging.getLogger(__name__)


class MainWindowBase(object):
    pass


class MainWindow(MainWindowBase, QMainWindow):
    def __init__(self):
        super().__init__()
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        load_ui_file(path, self)
