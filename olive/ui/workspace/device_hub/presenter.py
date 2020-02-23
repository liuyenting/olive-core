import logging
from abc import abstractmethod

from ..base import PresenterBase
from .view import DeviceHubView

__all__ = ["DeviceHubPresenter"]

logger = logging.getLogger(__name__)


class DeviceHubPresenter(PresenterBase):
    def __init__(self, view: DeviceHubView):
        super().__init__(view)

    ##

    #def update()


    ##

    def _register_view_callbacks(self):
        pass

