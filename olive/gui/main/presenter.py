import logging

from ..base import BasePresenter
from .view import BaseMainView
from .redirector import Workspace, WorkspaceRedirector

__all__ = ["MainPresenter"]

logger = logging.getLogger(__name__)


class MainPresenter(BasePresenter):
    def __init__(self, view: BaseMainView):
        super().__init__(view=view)

        self._redirector = WorkspaceRedirector()
        self.redirector.register_to(self.view)

        self.view.change_workspace.connect(self.on_change_workspace)

    ##

    @property
    def redirector(self) -> WorkspaceRedirector:
        return self._redirector

    ##

    def on_change_workspace(self, workspace: Workspace):
        workspace = self.redirector[workspace]
        self.view.set_current_workspace(workspace.view)
