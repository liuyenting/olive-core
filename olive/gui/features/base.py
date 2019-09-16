from PySide2.QtCore import Qt
from PySide2.QtWidgets import QDockWidget, QWidget

__all__ = ["Feature"]


class Feature(QDockWidget):
    """
    Base class for all the feature DockWidget.

    Arg:
        title (str): title of the dock widget

    Attribte:
        widget (QWidget): widget that holds actual components
    """

    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)

        self.setAllowedAreas(Qt.LeftDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetMovable)

        self.widget = QWidget()
        self.setWidget(self.widget)
