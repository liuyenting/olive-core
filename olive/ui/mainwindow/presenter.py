import logging
from abc import abstractmethod
from enum import IntEnum, auto
from collections.abc import Mapping

from ..base import BasePresenter
from ..workspace import (
    AcquisitionPresenter,
    DeviceHubPresenter,
    ProtocolEditorPresenter,
)
from .view import MainWindowView

__all__ = ["MainWindowPresenter", "Workspace"]

logger = logging.getLogger(__name__)


class Workspace(IntEnum):
    Acquisition = auto()
    DeviceHub = auto()
    ProtocolEditor = auto()


class WorkspaceRedirector(Mapping):
    def __init__(self):
        self._lut = {
            Workspace.Acquisition: AcquisitionPresenter,
            Workspace.DeviceHub: DeviceHubPresenter,
            Workspace.ProtocolEditor: ProtocolEditorPresenter,
        }

    def __getitem__(self, workspace: Workspace) -> int:
        index = self._lut[workspace]
        assert isinstance(index, int), "redirector has not register to a view yet"
        return index

    def __iter__(self):
        for workspace in self._lut.keys():
            yield workspace

    def __len__(self):
        return len(self._lut)

    ##

    def register_to(self, view: MainWindowView):
        for workspace, presenter_klass in self._lut.items():
            # create the presenter
            presenter = presenter_klass()
            # register to the view
            index = view.register_workspace_view(presenter.view)
            logger.debug(f'"{workspace.name}" assigned index {index}')
            # upate from classes to index
            self._lut[workspace] = index


class MainWindowPresenter(BasePresenter):
    def __init__(self):
        super().__init__()

        # popluate and register workspaces
        self._workspaces = WorkspaceRedirector()
        self._workspaces.register_to(self.view)

        # register callbacks
        self.view.set_change_workspace_action(self.on_change_workspace)
        self.view.set_exit_action(self.on_exit)

    ##

    ##

    def on_change_workspace(self, workspace: Workspace):
        index = self._workspaces[workspace]
        logger.debug(f'switch to workspace "{workspace.name}"')
        self.view.change_workspace(index)

    def on_exit(self):
        # TODO close everything and signal controller (maybe?)
        pass
