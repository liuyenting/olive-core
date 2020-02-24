from abc import abstractmethod
import logging
from typing import Callable
import os
from functools import partial

from qtpy.QtCore import Signal

from ..base import BaseQtView
from .presenter import Workspace

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowView(BaseQtView):
    change_workspace = Signal(Workspace)
    exit_triggered = Signal()

    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(path)

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

    def register_workspace_view(self, view: BaseQtView) -> int:
        """Add new workspace to workspace stacked widget."""
        index = self.workspace.addwidget(view)
        return index

    ##

    def set_current_workspace(self, index):
        self.workspace.setCurrentIndex(index)
