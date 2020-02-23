from __future__ import annotations
from abc import ABC

from .controller import Controller

__all__ = ["ViewBase", "PresenterBase"]


class ViewBase(ABC):
    def __init__(self, presenter: PresenterBase):
        self._presenter = presenter

    ##

    @property
    def presenter(self) -> PresenterBase:
        return self._presenter


class PresenterBase(ABC):
    def __init__(self):
        # retrieve view class from redirector
        view_klass = Controller().views[self]
        # create the view and pass presenter reference to it
        self._view = view_klass(self)

    ##

    @property
    def view(self) -> ViewBase:
        return self._view

    ##
