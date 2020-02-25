import logging

from qtpy.QtWidgets import QApplication

__all__ = ["launch"]

logger = logging.getLogger(__name__)


class AppController(object):
    pass


def launch():
    controller = AppController()

    # TODO launch service
