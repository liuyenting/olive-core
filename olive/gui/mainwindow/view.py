from abc import abstractmethod
import logging

from ..base import ViewBase

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowView(ViewBase):
    @abstractmethod
    def set_change_workspace_action(self, action):
        pass

    @abstractmethod
    def set_exit_action(self, action):
        pass

    @abstractmethod
    def add_workspace(self, view):
        pass

    ##

    @abstractmethod
    def change_workspace(self, index):
        pass
