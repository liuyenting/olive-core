import logging
from abc import abstractmethod
from enum import IntEnum, auto

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

        # populate workspaces
        self._workspaces = dict()
        self._register_workspaces()

    ##

    ##

    def on_change_workspace(self, portal: Portal):
        index = self._workspaces[portal][0]
        logger.debug(f'switch to workspace "{portal.name}"')
        self.view.change_workspace(index)

    @abstractmethod
    def on_exit(self):
        pass

    ##

    def _wire_connections(self):
        self.view.set_change_workspace_action(self.on_change_workspace)
        self.view.set_exit_action(self.on_exit)

    @abstractmethod
    def _register_workspaces(self):
        pass

    def _register_workspace(self, portal: Portal, presenter: PresenterBase):
        # register with the view
        index = self.view.add_workspace(presenter.view)
        logger.debug(f"{portal.name} assigned index {index}")
        # save presenter
        self._workspaces[portal] = (index, presenter)
