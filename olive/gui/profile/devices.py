import logging

from PySide2 import QtWidgets

__all__ = ['DevicesPage']

class DevicesPage(QtWidgets.QWizardPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.setTitle("Devices")
        self.setSubTitle("Please assign which hardwares will perform these steps.")
