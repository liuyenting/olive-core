import logging
from abc import abstractmethod

from qtpy.QtCore import Signal

from ..base import BaseView

__all__ = []

logger = logging.getLogger(__name__)


class BaseDeviceHubView(BaseView):
    refresh_device_list = Signal()
    select_device = Signal(str)

    refresh_parameters = Signal(str)

    ##

    @abstractmethod
    def add_category(self, name):
        """Add new device category to the list."""

    @abstractmethod
    def remove_category(self, name):
        """
        Remove a device category from the list.

        This will also remove all the associated drivers.
        """

    @abstractmethod
    def add_device(self, device):
        pass

    @abstractmethod
    def remove_device(self, device):
        pass

    ##


class BaseDeviceHubView(BaseDeviceHubView):
    pass
