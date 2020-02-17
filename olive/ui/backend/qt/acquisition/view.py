import logging
import os

from olive.ui.acquisition import AcquisitionView as _AcquisitionView
from ..base import QWidgetViewBase

__all__ = ["AcquisitionView"]

logger = logging.getLogger(__name__)


class AcquisitionView(_AcquisitionView, QWidgetViewBase):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(path)

