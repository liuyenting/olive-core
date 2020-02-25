import logging
import os
from abc import abstractmethod
from typing import Optional
from enum import IntEnum, auto

from qtpy.QtCore import Signal

from olive.devices.base import Device
from ...base import BaseView

__all__ = ["DeviceHubView"]

logger = logging.getLogger(__name__)


class CategoryState(IntEnum):
    Searching = auto()
    Ready = auto()


class BaseDeviceHubView(BaseView):
    refresh_device_list = Signal()
    select_device = Signal(str)

    refresh_properties = Signal()  # FIXME assign device name to refresh

    ##
    # device list manipulation - category

    @abstractmethod
    def add_category(self, category: Device):
        """Add new device category."""

    @abstractmethod
    def remove_category(self, category: Optional[Device] = None):
        """
        Remove a device category.

        Args:
            category (Device, optional): remove this category from the list, if `None`,
                remove all categories.
        """

    @abstractmethod
    def set_category_state(self, category: Device, state: CategoryState):
        """Set category state."""

    @abstractmethod
    def set_device_list_refresh_state(self, enable: bool):
        """Set whether user can trigger device list refresh."""

    ##
    # device list manipulation - device

    @abstractmethod
    def add_device(self, category, device: Device):
        pass

    @abstractmethod
    def remove_device(self, category, device: Device):
        pass

    ##


class DeviceHubView(BaseDeviceHubView):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(ui_path=path)

        # device list
        self.refresh_devices_button.clicked.connect(self.refresh_device_list.emit)

        # property editor
        self.refresh_properties_button.setEnabled(False)  # nothing selected at start
        self.refresh_properties_button.clicked.connect(self.refresh_properties.emit)
        # FIXME when signal is patched, add missing device UUID assignment

    ##
    # device list maipulation - category

    def add_category(self, category: Device):
        pass

    def remove_category(self, category: Optional[Device] = None):
        pass

    def set_category_state(self, category: Device, state: CategoryState):
        pass

    def set_device_list_refresh_state(self, enable: bool):
        self.refresh_devices_button.setEnabled(enable)

    ##
