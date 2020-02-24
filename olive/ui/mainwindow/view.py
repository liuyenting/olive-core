from abc import abstractmethod
import logging
import os
from functools import partial

from qtpy.QtCore import Signal

from ..base import BaseView
from .redirector import Workspace

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowBaseView(BaseView):
    change_workspace = Signal(Workspace)
    exit_triggered = Signal()

    ##

    @abstractmethod
    def register_workspace_view(self, workspace: Workspace, view: BaseView) -> int:
        """Add new workspace."""

    ##

    @abstractmethod
    def set_current_workspace(self, workspace: Workspace):
        """Set current visible workspace."""


class MainWindowView(MainWindowBaseView):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(path)

        self._workspace_id = dict()

        # workspace buttons
        mapping = {
            self.device_hub.clicked: Workspace.DeviceHub,
            self.protocol_editor.clicked: Workspace.ProtocolEditor,
            self.acquisition.clicked: Workspace.Acquisition,
        }
        for signal, workspace in mapping.items():
            signal.connect(partial(self.change_workspace.emit, workspace))

        # exit actions
        self.exit.clicked.connect(self.exit_triggered.emit)

    ##

    def register_workspace_view(self, workspace: Workspace, view: BaseView) -> int:
        """Add new workspace to workspace stacked widget."""
        index = self.workspace.addwidget(view)
        logger.debug(f'"{workspace.name}" assigned index {index}')
        self._workspace_id[workspace] = index

    ##

    def set_current_workspace(self, workspace: Workspace):
        index = self._workspace_id[workspace]
        self.workspace.setCurrentIndex(index)
