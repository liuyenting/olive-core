from PySide2.QtWidgets import QDockWidget

__all__ = ["Feature"]


class Feature(QDockWidget):
    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)

        self.setFeatures(QDockWidget.DockWidgetMovable)

