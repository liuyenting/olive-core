from qtpy.uic import loadUi

from . import resources_rc

__all__ = ["load_ui_file"]


def load_ui_file(path, parent=None):
    """
    Load a Qt Designer .ui file and returns an instance of the user interface.

    Args:
        path (str): absolute path to .ui file
        parent (QWidget): the widget into which UI widgets are loaded

    Returns:
        QWidget: the base instance

    Reference:
        https://github.com/mottosso/Qt.py/tree/master/examples/loadUi
    """
    ui = loadUi(path)
    if parent is not None:
        for member in dir(ui):
            if not member.startswith("__") and member != "staticMetaObject":
                setattr(parent, member, getattr(ui, member))
    return ui
