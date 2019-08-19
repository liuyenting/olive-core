from PySide2.QtWidgets import QMainWindow, QToolBar

__all__ = ["Hub"]


class Hub(QMainWindow):
    def __init__(self, title="Olive"):
        super().__init__()

        self.init()

    def init(self):
        exitAction = QAction(QI)
        self._toolbar = self.addToolBar('Exit')
        self._toolbar.addAction(exitAction)

    @property
    def menu_bar(self):
        return self._menu_bar
