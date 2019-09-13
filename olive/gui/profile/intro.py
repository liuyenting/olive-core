import logging

from PySide2 import QtWidgets

__all__ = ["IntroPage"]


class IntroPage(QtWidgets.QWizardPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.setTitle("Intro")
        self.setSubTitle("")

    def initializePage(self):
        pass