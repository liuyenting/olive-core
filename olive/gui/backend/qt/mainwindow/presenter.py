import logging

from olive.gui.mainwindow import MainWindowPresenter as _MainWindowPresenter
from olive.gui.mainwindow import Portal

from ..acquisition import AcquisitionPresenter
from ..devicehub import DeviceHubPresenter
from .view import MainWindowView

__all__ = ["MainWindowPresenter"]

logger = logging.getLogger(__name__)


class MainWindowPresenter(_MainWindowPresenter):
    def __init__(self):
        view = MainWindowView()
        super().__init__(view)

        self.register_workspaces()

        # this is the primary window, show it
        view.show()

    ##

    def register_workspaces(self):
        # self.view.set_workspace(Portal.DeviceHub, DeviceHubView)
        # self.view.set_workspace(Portal.ProtocolEditor, ProtocolEditorView)
        self.view.set_workspace(Portal.Acquisition, AcquisitionView)

    ##

    def on_change_workspace(self, portal: Portal):
        logger.debug(f'change workspace to "{portal.name}"')

    def on_exit(self):
        pass
