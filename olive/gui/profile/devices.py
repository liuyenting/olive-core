import logging

from PySide2 import QtWidgets

__all__ = ["DevicesPage"]


class DevicesPage(QtWidgets.QWizardPage):
    def __init__(self):
        super().__init__()

        self.setTitle("Devices")
        self.setSubTitle("Please assign which hardwares will perform these steps.")

    def initializePage(self):
        pass
