import logging
import os
from abc import ABCMeta, abstractmethod

from qtpy.QtCore import QObject
from qtpy.QtWidgets import QWidget
from qtpy.uic import loadUi

__all__ = ["BaseView"]

logger = logging.getLogger(__name__)


class QABCMeta(ABCMeta, type(QObject)):
    """
    Mixin class of ABCMeta and QObjectType.

    FIXME ABCMeta fail to do its magic for @abstracmethod dunno why
    """


class BaseView(QWidget, metaclass=QABCMeta):
    """
    Base class for views.

    Args:
        ui_path (str): path to the Qt Designer .ui file
    """

    def __init__(self, ui_path: str):
        super().__init__()

        logger.debug(f'load UI definition from "{os.path.basename(ui_path)}"')
        loadUi(ui_path, self)
