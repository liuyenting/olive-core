import logging

from PySide2 import QtWidgets

__all__ = ["SummaryPage"]


class SummaryPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Summary")

    def initializePage(self):
        pass