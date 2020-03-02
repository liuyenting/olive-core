import logging
import os

from olive.gui.base import BaseView

__all__ = ["ProtocolEditorView"]

logger = logging.getLogger(__name__)


class BaseProtocolEditorView(BaseView):
    pass


class ProtocolEditorView(BaseProtocolEditorView):
    def __init__(Self):
        path = os.path.join(os.path.dirname(__file__), "view.ui")
        super().__init__(ui_path=path)
