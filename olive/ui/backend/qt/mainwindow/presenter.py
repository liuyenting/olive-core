import logging

from olive.ui.mainwindow import MainWindowPresenter as _MainWindowPresenter
from olive.ui.mainwindow import Portal

from ..acquisition import AcquisitionPresenter
from ..devicehub import DeviceHubPresenter
from ..protoedit import ProtocolEditorPresenter
from .view import MainWindowView

__all__ = ["MainWindowPresenter"]

logger = logging.getLogger(__name__)


class MainWindowPresenter(_MainWindowPresenter):
    def __init__(self):
        view = MainWindowView()
        super().__init__(view)

        view.show()

    ##

    ##

    def on_exit(self):
        logger.debug(f"mainwindow on_exit()")
        # TODO check system states
        self.view.close()

    ##

    def _register_workspaces(self):
        self._register_workspace(Portal.DeviceHub, DeviceHubPresenter())
        self._register_workspace(Portal.ProtocolEditor, ProtocolEditorPresenter())
        self._register_workspace(Portal.Acquisition, AcquisitionPresenter())
