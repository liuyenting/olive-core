from .view import BaseView

__all__ = ["BasePresenter"]


class BasePresenter(object):
    def __init__(self, view: BaseView):
        view.presenter = self
        self._view = view

    ##

    @property
    def view(self) -> BaseView:
        return self._view
