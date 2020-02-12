from functools import partial
import logging
import os

from olive.gui.mainwindow import MainWindowView as _MainWindowView
from olive.gui.mainwindow import Portal

from ..base import QMainWindowViewBase

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowView(_MainWindowView, QMainWindowViewBase):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(path)

        self._workspace_index_lut = dict()

    ##

    def set_change_workspace_action(self, action):
        self.device_hub.clicked.connect(partial(action, Portal.DeviceHub))
        self.protocol_editor.clicked.connect(partial(action, Portal.ProtocolEditor))
        self.acquisition.clicked.connect(partial(action, Portal.Acquisition))

    def set_workspace(self, portal: Portal, view):
        index = self.workspace.addWidget(view)
        assert (
            portal not in self._workspace_index_lut
        ), f'portal "{portal.name}" already assigned a workspace'
        self._workspace_index_lut[portal] = index

    ##

    def change_workspace(self, portal: Portal):
        index = self._workspace_index_lut[portal]
        self.workspace.setCurrentIndex(index)

