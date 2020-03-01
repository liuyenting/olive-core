import logging
import os
from abc import abstractmethod
from typing import Optional
from enum import IntEnum, auto

from qtpy.QtCore import Signal
from qtpy.QtGui import QIcon, QPixmap
from qtpy.QtWidgets import QTreeWidgetItem

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
    # device list - manipulate categories

    @abstractmethod
    def set_hostname(self, hostname: str):
        """Set device list root node to reflect connected host."""
        pass

    @abstractmethod
    def add_device_class(self, device_class: str):
        """Add new device class."""

    @abstractmethod
    def remove_device_class(self, device_class: Optional[str] = None):
        """
        Remove a device class.

        Args:
            category (str, optional): remove this category from the list, if `None`,
                remove all categories.
        """

    @abstractmethod
    def set_category_state(self, category: Device, state: CategoryState):
        """Set category state."""

    @abstractmethod
    def set_device_list_refresh_state(self, enable: bool):
        """Set whether user can trigger device list refresh."""

    ##
    # device list - manipulate devices

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
    # device list - manipulate categories

    def set_hostname(self, hostname: str):
        n_toplevel = self.device_list.topLevelItemCount()
        if n_toplevel > 0:
            # modify existing top level item
            assert n_toplevel == 1, "multi-host is not supported"
            root = self.device_list.topLevelItem(0)
        else:
            # create top level item
            root = QTreeWidgetItem(self.device_list)
            # add icon
            icon = QIcon()
            icon.addPixmap(QPixmap(":/device_hub/computer"), QIcon.Normal, QIcon.Off)
            root.setIcon(0, icon)

        root.setText(0, hostname)

    def add_device_class(self, device_class: str):
        """Add new device class."""
        # TODO create widget item
        # TODO lookup icons
        # TODO assign text and icons

    def remove_device_class(self, device_class: Optional[str] = None):
        """
        Remove a device class.

        Args:
            category (str, optional): remove this category from the list, if `None`,
                remove all categories.
        """

    def set_category_state(self, category: Device, state: CategoryState):
        pass

    def set_device_list_refresh_state(self, enable: bool):
        self.refresh_devices_button.setEnabled(enable)

    ##
    # property editor
