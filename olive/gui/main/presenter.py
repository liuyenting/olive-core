import logging

from ..base import BasePresenter
from ..workspace import Workspace
from .redirector import WorkspaceRedirector
from .view import BaseMainView

__all__ = ["MainPresenter"]

logger = logging.getLogger(__name__)


class MainPresenter(BasePresenter):
    def __init__(self, view: BaseMainView):
        super().__init__(view=view)

        self._redirector = WorkspaceRedirector()
        self.redirector.register_to(self.view)

        self.view.change_workspace.connect(self.on_change_workspace)
        self.view.exit_triggered.connect(self.on_exit)

    ##

    @property
    def redirector(self) -> WorkspaceRedirector:
        return self._redirector

    ##

    def on_change_workspace(self, workspace: Workspace):
        workspace = self.redirector[workspace]
        self.view.set_current_workspace(workspace.view)

    def on_exit(self):
        print(">>> EXIT <<<")
        self.view.close()
