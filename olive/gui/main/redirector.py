from collections.abc import Mapping
from enum import IntEnum, auto

from .view import BaseMainView

__all__ = ["Workspace", "WorkspaceRedirector"]


class Workspace(IntEnum):
    DeviceHub = auto()  # 1)
    ProtocolEditor = auto()  # 2)
    Acquisition = auto()  # 3)


class WorkspaceRedirector(Mapping):
    def __init__(self):
        self._workspaces = {
            Workspace.DeviceHub: (None, None),
            Workspace.ProtocolEditor: (None, None),
            Workspace.Acquisition: (None, None),
        }

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

    def register_to(self, view: BaseMainView):
        for workspace, (p_klass, v_klass) in self._workspaces.items():
            # create presenter/view
            view = v_klass()
            presenter = p_klass(view)
            # register
            view.register_workspace_view(view)
            # update the record
            self._workspaces[workspace] = presenter
