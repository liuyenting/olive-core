from abc import ABCMeta

from .view import BaseView

__all__ = ["BasePresenter"]


class BasePresenter(metaclass=ABCMeta):
    def __init__(self, view: BaseView):
        self._view = view

    ##

    @property
    def view(self) -> BaseView:
        return self._view
