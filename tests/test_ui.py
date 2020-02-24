from qtpy.QtWidgets import QApplication

import coloredlogs

from olive.ui.base import BasePresenter, BaseQtView

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

app = QApplication()

view = BaseQtView()
presenter = BasePresenter(view)
