import logging

from olive.utils import Singleton

from .mainwindow import MainWindowPresenter
from .view_factory import ViewFactory

__all__ = ["Controller"]

logger = logging.getLogger(__name__)


class Controller(metaclass=Singleton):
    """
    App controller manages the background service and presenter/view instantiation.

    Args:
        backend (str): name of the backend to use
    """

    def __init__(self, backend: str):
        # retrieve backend
        views = ViewFactory.__subclasses__()
        views = {klass.name: klass for klass in views}
        logger.debug(f"found {len(views)} view factory")

        try:
            self._views = views[backend]()  # instantiation
        except KeyError:
            logger.error(f'unknown backend "{backend}"')

    ##

    @property
    def views(self) -> ViewFactory:
        return self._views

    ##

    def run(self):
        """
        Primary entry point for the application.
            1) Start background acquisition service.
            2) Create user interface.
        """

        # TODO kick start background service

        main_window = MainWindowPresenter()

        # TODO link main window with model/interactor

