import logging

from ...base import BasePresenter
from .view import BaseDeviceHubView

__all__ = ["DeviceHubPresenter"]

logger = logging.getLogger(__name__)


class DeviceHubPresenter(BasePresenter):
    def __init__(self, view: BaseDeviceHubView):
        super().__init__(view=view)

        self.view.refresh_device_list.connect(self.on_refresh_device_list)
        # self.view.select_device.connect(self.on_select_device)

        self.view.refresh_properties.connect(self.on_refresh_properties)

        # TODO trigger refresh

    ##

    ##

    def on_refresh_device_list(self):
        print("refresh device list")

    def on_select_device(self):
        print("select device")

    ##

    def on_refresh_properties(self):
        print("refresh properties")