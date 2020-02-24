from enum import IntEnum, auto
from collections.abc import Mapping

from ..base import BaseView

__all__ = ["Workspace", "WorkspaceRedirector"]


class Workspace(IntEnum):
    Acquisition = auto()
    DeviceHub = auto()
    ProtocolEditor = auto()


class WorkspaceRedirector(Mapping):
    def __init__(self):
        self._lut = {
            # Workspace.Acquisition: AcquisitionPresenter,
            # Workspace.DeviceHub: DeviceHubPresenter,
            # Workspace.ProtocolEditor: ProtocolEditorPresenter,
        }

    def __getitem__(self, workspace: Workspace) -> int:
        presenter = self._lut[workspace]
        return presenter

    def __iter__(self):
        for workspace in self._lut.keys():
            yield workspace

    def __len__(self):
        return len(self._lut)

    ##

    def register_to(self, view: BaseView):
        for workspace, presenter_klass in self._lut.items():
            # create the presenter
            presenter = presenter_klass()
            # register to the view
            view.register_workspace_view(presenter.view)
            # upate from classes to actual object
            self._lut[workspace] = presenter
