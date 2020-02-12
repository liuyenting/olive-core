import logging
import os

from olive.gui.devicehub import DeviceHubView as _DeviceHubView
from ..base import QWidgetViewBase

__all__ = ["DeviceHubView"]

logger = logging.getLogger(__name__)


class DeviceHubView(_DeviceHubView, QWidgetViewBase):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(path)

