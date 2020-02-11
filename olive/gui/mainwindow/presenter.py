import logging
from abc import ABC, abstractmethod
from enum import IntEnum, auto

from ..base import PresenterBase

__all__ = ["MainWindowPresenter", "Portal"]

logger = logging.getLogger(__name__)


class Portal(IntEnum):
    DeviceHub = auto()
    ProtocolEditor = auto()
    Acquisition = auto()


class MainWindowPresenter(PresenterBase):
    @abstractmethod
    def on_change_workspace(self, portal: Portal):
        pass

    @abstractmethod
    def on_exit(self):
        pass
