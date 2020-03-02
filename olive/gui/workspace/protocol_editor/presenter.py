import logging

from olive.gui.base import BasePresenter

from .view import BaseProtocolEditorView

__all__ = ["ProtocolEditorPresenter"]

logger = logging.getLogger(__name__)


class ProtocolEditorPresenter(BasePresenter):
    def __init__(self, view: BaseProtocolEditorView):
        super().__init__(view=view)
