from abc import abstractmethod

__all__ = ["ViewBase", "PresenterBase"]


class ViewBase(object):
    pass


class PresenterBase(object):
    def __init__(self, view: ViewBase):
        self._view = view
        self.wire_connections()

    ##

    @property
    def view(self):
        return self._view

    ##

    @abstractmethod
    def wire_connections(self):
        pass
