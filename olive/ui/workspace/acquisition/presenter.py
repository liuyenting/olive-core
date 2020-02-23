import logging
from abc import abstractmethod

from ..base import PresenterBase
from .view import AcquisitionView

__all__ = ["AcquisitionPresenter"]

logger = logging.getLogger(__name__)


class AcquisitionPresenter(PresenterBase):
    def __init__(self, view: AcquisitionView):
        super().__init__(view)

    def wire_connections(self):
        pass

    ##

