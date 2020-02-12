import logging
from abc import abstractmethod
from enum import IntEnum, auto

from ..acquisition import AcquisitionView
from ..base import PresenterBase
from .view import MainWindowView

__all__ = ["MainWindowPresenter", "Portal"]

logger = logging.getLogger(__name__)


class Portal(IntEnum):
    DeviceHub = auto()
    ProtocolEditor = auto()
    Acquisition = auto()


class MainWindowPresenter(PresenterBase):
    def __init__(self, view: MainWindowView):
        super().__init__(view)

    ##

    def wire_connections(self):
        self.view.set_change_workspace(self.on_change_workspace)

    ##

    @abstractmethod
    def on_change_workspace(self, portal: Portal):
        pass

    @abstractmethod
    def on_exit(self):
        pass

