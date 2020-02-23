import logging
from abc import abstractmethod

from ..base import PresenterBase
from .view import ProtocolEditorView

__all__ = ["ProtocolEditorPresenter"]

logger = logging.getLogger(__name__)


class ProtocolEditorPresenter(PresenterBase):
    def __init__(self, view: ProtocolEditorView):
        super().__init__(view)

    def wire_connections(self):
        pass

    ##

