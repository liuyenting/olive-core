from abc import abstractmethod
import logging
from typing import Callable

from ..base import ViewBase
from .presenter import Portal

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowView(ViewBase):
    @abstractmethod
    def set_change_workspace_action(self, action: Callable[[Portal], None]):
        pass

    @abstractmethod
    def set_exit_action(self, action: Callable[[], None]):
        pass

    @abstractmethod
    def register_workspace_view(self, view: ViewBase) -> int:
        pass

    ##

    @abstractmethod
    def change_workspace(self, index):
        pass
