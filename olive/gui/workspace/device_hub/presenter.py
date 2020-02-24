import logging

from ..base import BasePresenter
from .view import BaseDeviceHubView

__all__ = []

logger = logging.getLogger(__name__)


class DeviceHubPresenter(BasePresenter):
    def __init__(self, view: BaseDeviceHubView):
        super().__init__(view=view)

        self.view.refresh_device_list.connect(self.on_refresh_device_list)
        self.view.select_device.connect(self.on_select_device)

        self.view.on_refresh_paramters(self.on_refresh_paramters)

    ##

    ##

    def on_refresh_device_list(self):
        pass

    def on_select_device(self):
        pass

    ##

    def on_refresh_paramters(self):
        pass
