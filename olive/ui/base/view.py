from abc import ABCMeta
import logging
import os

from qtpy.QtCore import QObject
from qtpy.QtWidgets import QWidget
from qtpy.uic import loadUi


__all__ = ["BaseView"]
logger = logging.getLogger(__name__)


class QABCMeta(ABCMeta, type(QObject)):
    """
    Mixing metaclass to ensure we can have both ABC and QWidget.

    FIXME ABCMeta does not enforce abstractmethod labeled functions being overwritten
    """


class BaseView(QWidget, metaclass=QABCMeta):
    def __init__(self, ui_path: str):
        super().__init__()

        logger.debug(f'creating Qt view from "{os.path.basename(ui_path)}"')
        loadUi(ui_path, self)
