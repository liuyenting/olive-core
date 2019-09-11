import logging

from PySide2 import QtWidgets

__all__ = ['ScriptPage']


class ScriptPage(QtWidgets.QWizardPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.setTitle("Script")
        self.setSubTitle(
            "Please select a script that can describe the necessary acquisition steps."
        )

