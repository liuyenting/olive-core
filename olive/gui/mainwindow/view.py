from abc import ABC, abstractmethod
import logging

from ..base import ViewBase
from .presenter import Portal

__all__ = ["MainWindowView"]

logger = logging.getLogger(__name__)


class MainWindowView(ViewBase):
    @abstractmethod
    def set_change_workspace(self, portal: Portal):
        pass

