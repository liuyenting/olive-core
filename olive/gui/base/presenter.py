from abc import ABCMeta

from ..data import DataManager
from .view import BaseView

__all__ = ["BasePresenter"]


class BasePresenter(metaclass=ABCMeta):
    def __init__(self, view: BaseView):
        self._dm = DataManager()
        self._view = view

    ##

    @property
    def data_manager(self) -> DataManager:
        return self._dm

    @property
    def view(self) -> BaseView:
        return self._view
