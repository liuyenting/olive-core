from collections.abc import Mapping

from ..workspace.mapping import Workspace, workspace_defs
from .view import BaseMainView

__all__ = ["Workspace", "WorkspaceRedirector"]


class WorkspaceRedirector(Mapping):
    def __init__(self):
        self._workspaces = workspace_defs.copy()

    def __getitem__(self, workspace: Workspace):
        presenter = self._workspaces[workspace]
        assert not isinstance(
            presenter, tuple
        ), "redirector is not registered to a view yet"
        return presenter

    def __iter__(self):
        for workspace in self._workspaces.keys():
            yield workspace

    def __len__(self):
        return len(self._workspaces)

    ##

    def register_to(self, main_view: BaseMainView):
        for workspace, klass_def in self._workspaces.items():
            # create presenter/view
            view = klass_def.view()
            presenter = klass_def.presenter(view)
            # register
            main_view.register_workspace_view(view)
            # update the record
            self._workspaces[workspace] = presenter
