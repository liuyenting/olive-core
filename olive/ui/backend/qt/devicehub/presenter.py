import logging

from olive.ui.devicehub import DeviceHubPresenter as _DeviceHubPresenter

from .view import DeviceHubView

__all__ = ["DeviceHubPresenter"]

logger = logging.getLogger(__name__)


class DeviceHubPresenter(_DeviceHubPresenter):
    def __init__(self):
        view = DeviceHubView()
        super().__init__(view)

    ##

