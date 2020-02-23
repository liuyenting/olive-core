import logging

from .controller import Controller

__all__ = ["launch"]

logger = logging.getLogger(__name__)

# TODO wrap launch() with clicks
def launch(backend="qt"):
    controller = Controller(backend)
    controller.run()
