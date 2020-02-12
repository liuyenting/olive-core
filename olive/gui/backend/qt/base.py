from qtpy.QtWidgets import QMainWindow, QWidget
from qtpy.uic import loadUi

# mandatory import for uic files, early cached
from . import resources_rc  # noqa

__all__ = ["QMainWindowViewBase", "QWidgetViewBase"]


class QMainWindowViewBase(QMainWindow):
    def __init__(self, path):
        super().__init__()
        loadUi(path, self)


class QWidgetViewBase(QWidget):
    def __init__(self, path):
        super().__init__()
        loadUi(path, self)
