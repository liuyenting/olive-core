import logging
import os

from qtpy.QtWidgets import QWidget

from ..utils import load_ui_file

__all__ = ["Acquisition"]

logger = logging.getLogger(__name__)


class Acquisition(QWidget):
    def __init__(self):
        super().__init__()
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        load_ui_file(path, self)
