import logging

from PySide2 import QtWidgets

__all__ = ['ScriptPage']


class ScriptPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Script")
        self.setSubTitle(
            "Please select a script that can describe the necessary acquisition steps."
        )

    def initializePage(self):
        pass

