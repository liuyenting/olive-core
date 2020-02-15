import logging
import os

from olive.ui.protoedit import ProtocolEditorView as _ProtocolEditorView
from ..base import QWidgetViewBase

__all__ = ["ProtocolEditorView"]

logger = logging.getLogger(__name__)


class ProtocolEditorView(_ProtocolEditorView, QWidgetViewBase):
    def __init__(self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(path)
