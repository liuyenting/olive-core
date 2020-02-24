import logging
import os
from abc import abstractmethod
from functools import partial

from qtpy.QtCore import Signal

from ..base import BaseView
from .redirector import Workspace

__all__ = ["MainView"]

logger = logging.getLogger(__name__)


class BaseMainView(BaseView):
    change_workspace = Signal(BaseView)
    exit_triggered = Signal()

    ##

    @abstractmethod
    def register_workspace_view(self, view: BaseView):
        """Register a new workspace view for background switching."""

    ##

    @abstractmethod
    def set_current_workspace(self, view: BaseView):
        """Change current workspace to another one."""


class MainView(BaseMainView):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(ui_path=path)

        # workspace buttons
        mapping = {
            self.view.device_hub.clicked: Workspace.DeviceHub,
            self.view.protocol_editor.clicked: Workspace.ProtocolEditor,
            self.view.acquisition.clicked: Workspace.Acquisition,
        }
        for signal, workspace in mapping.items():
            signal.connect(partial(self.change_workspace.emit, workspace))

    ##

    def register_workspace_view(self, view: BaseView):
        self.workspace.addWidget(view)
        logger.debug(f'workspace "{view}" registered')

    ##

    def set_current_workspace(self, view: BaseView):
        self.workspace.setCurrentWidget(view)
