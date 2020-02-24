from abc import ABCMeta, abstractmethod, ABC
import logging
import os

from qtpy.QtWidgets import QWidget
from qtpy.uic import loadUi


__all__ = ["BaseView", "BaseQtView"]
logger = logging.getLogger(__name__)


class QtABCMeta(ABCMeta, type(QWidget)):
    """Mixing metaclass to ensure we can have both ABC and QWidget."""


class BaseView(ABC, metaclass=QtABCMeta):
    @abstractmethod
    def test_func(self):
        pass


class BaseQtView(BaseView, QWidget):
    def __init__(self, ui_path: str):
        super().__init__()
        # loadUi(ui_path, self)
        logger.debug(f'creating Qt view from "{os.path.basename(ui_path)}"')

