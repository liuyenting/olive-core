from PySide2.QtWidgets import QDockWidget


class TimeSeriesWidget(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Time Series')

        self.setFeatures(QDockWidget.DockWidgetMovable)

