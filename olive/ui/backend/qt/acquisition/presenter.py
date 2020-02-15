import logging

from olive.ui.acquisition import AcquisitionPresenter as _AcquisitionPresenter

from .view import AcquisitionView

__all__ = ["AcquisitionPresenter"]

logger = logging.getLogger(__name__)


class AcquisitionPresenter(_AcquisitionPresenter):
    def __init__(self):
        view = AcquisitionView()
        super().__init__(view)

    ##

