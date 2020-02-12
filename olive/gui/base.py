from abc import abstractmethod

__all__ = ["ViewBase", "PresenterBase"]


class ViewBase(object):
    pass


class PresenterBase(object):
    def __init__(self, view: ViewBase):
        self._view = view
        self._wire_connections()

    ##

    @property
    def view(self):
        return self._view

    ##

    @abstractmethod
    def _wire_connections(self):
        pass
