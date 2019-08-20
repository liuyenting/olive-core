import logging
import os

from PySide2.QtGui import QIcon

__all__ = ["ICON"]

logger = logging.getLogger(__name__)
cwd = os.path.dirname(os.path.abspath(__file__))


def ICON(name, root=None):
    """
    Retrieve a QIcon.
    
    - https://favicon.io/favicon-generator/ , Noto Sans
    """
    if not root:
        root = os.path.join(cwd, 'resources')
    return QIcon(os.path.join(root, name))
