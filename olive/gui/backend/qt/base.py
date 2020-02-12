from qtpy.QtWidgets import QMainWindow, QWidget

from olive.gui.base import ViewBase

from .utils import load_ui_file

__all__ = ["QtViewBase", "QMainWindowViewBase", "QWidgetViewBase"]


class QtViewBase(ViewBase):
    def __init__(self, path):
        super().__init__()
        load_ui_file(path, self)


class QMainWindowViewBase(QtViewBase, QMainWindow):
    def __init__(self, path):
        super().__init__(path)


class QWidgetViewBase(QtViewBase, QWidget):
    def __init__(self, path):
        super().__init__(path)
