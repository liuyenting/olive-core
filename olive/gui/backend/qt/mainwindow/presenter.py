import logging

from olive.gui.mainwindow import MainWindowPresenter as _MainWindowPresenter
from olive.gui.mainwindow import Portal, MainWindowView

__all__ = ["MainWindowPresenter"]

logger = logging.getLogger(__name__)


class MainWindowPresenter(_MainWindowPresenter):
    def __init__(self, view: MainWindowView):
        super().__init__(view)

        self.view.set_change_workspace(self.on_change_workspace)

        # this is the primary window, show it
        view.show()

    ##

    def on_change_workspace(self, portal: Portal):
        logger.debug(f'change workspace to "{portal.name}"')

    def on_exit(self):
        pass
