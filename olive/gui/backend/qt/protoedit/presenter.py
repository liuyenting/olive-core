import logging

from olive.gui.protoedit import ProtocolEditorPresenter as _ProtocolEditorPresenter

from .view import ProtocolEditorView

__all__ = ["ProtocolEditorPresenter"]

logger = logging.getLogger(__name__)


class ProtocolEditorPresenter(_ProtocolEditorPresenter):
    def __init__(self):
        view = ProtocolEditorView()
        super().__init__(view)

    ##

