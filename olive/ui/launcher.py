import logging

from .controller import Controller

__all__ = ["launch"]

logger = logging.getLogger(__name__)

# TODO wrap launch() with clicks


def launch():
    print('launch start')
    controller = Controller()
    print('controller created')
    controller.run()
