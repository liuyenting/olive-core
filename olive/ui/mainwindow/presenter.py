import logging
from abc import abstractmethod

from ..base import BasePresenter, BaseView

"""
from ..workspace import (
    AcquisitionPresenter,
    DeviceHubPresenter,
    ProtocolEditorPresenter,
)
"""
from .redirector import Workspace, WorkspaceRedirector

__all__ = ["MainWindowPresenter", "Workspace"]

logger = logging.getLogger(__name__)


class MainWindowPresenter(BasePresenter):
    def __init__(self, view: BaseView):
        super().__init__()

        # popluate and register workspaces
        self._workspaces = WorkspaceRedirector()
        self._workspaces.register_to(self.view)

        # register callbacks
        self.view.change_workspace.connect(self.on_change_workspace)
        self.view.exit_triggered.connect(self.on_exit)

    ##

    ##

    def on_change_workspace(self, workspace: Workspace):
        logger.debug(f'switch to workspace "{workspace.name}"')
        self.view.change_workspace(workspace)

    def on_exit(self):
        # TODO close everything and signal controller (maybe?)
        pass
