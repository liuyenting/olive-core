from abc import abstractmethod
import logging

from ..base import ViewBase

__all__ = ["DeviceHubView"]

logger = logging.getLogger(__name__)


class DeviceHubView(ViewBase):
    @abstractmethod
    def add_category(self, category):
        pass

    @abstractmethod
    def add_driver(self, driver):
        pass

