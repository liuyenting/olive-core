from abc import abstractmethod
import logging

from ..base import ViewBase
from .presenter import Portal

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowView(ViewBase):
    @abstractmethod
    def set_change_workspace_action(self, action):
        pass

    @abstractmethod
    def set_workspace(self, portal: Portal, view):
        """Set portal/workspace association."""
        pass

    ##

    @abstractmethod
    def change_workspace(self, portal: Portal):
        pass
