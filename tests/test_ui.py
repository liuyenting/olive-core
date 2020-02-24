from abc import ABC

from qtpy.QtWidgets import QApplication

import coloredlogs
from qtpy.QtCore import Signal

from olive.ui.base import BasePresenter, BaseView

coloredlogs.install(
    level="DEBUG", fmt="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S"
)

app = QApplication()


class Derived(ABC, BaseView):
    speak = Signal(str)


def say(message):
    print(f'say "{message}"')


view = Derived("hello")
view.speak.connect(say)
view.speak.emit("bullshit")
presenter = BasePresenter(view)
