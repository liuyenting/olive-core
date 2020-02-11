class ViewBase(object):
    pass


class PresenterBase(object):
    def __init__(self, view: ViewBase):
        self._view = view

    ##

    @property
    def view(self):
        return self._view

