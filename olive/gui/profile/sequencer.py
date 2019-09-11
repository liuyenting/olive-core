import logging

from PySide2 import QtWidgets

__all__ = ['SequencerPage']

class SequencerPage(QtWidgets.QWizardPage):
    def __init__(self, parent):
        super().__init__(parent)

        self.setTitle("Sequencer")
        self.setSubTitle("Please decide how the execution steps will be regulated.")

