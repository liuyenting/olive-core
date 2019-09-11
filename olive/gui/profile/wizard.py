import logging

from PySide2 import QtWidgets

from olive.gui.profile import IntroPage, ScriptPage, SequencerPage, DevicesPage

__all__ = ["ProfileWizard"]

logger = logging.getLogger(__name__)


class ProfileWizard(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()

        self.addPage(IntroPage(self))
        self.addPage(ScriptPage(self))
        self.addPage(SequencerPage(self))
        self.addPage(DevicesPage(self))


if __name__ == "__main__":
    from PySide2 import QtWidgets

    app = QtWidgets.QApplication()
    wizard = ProfileWizard()

    wizard.setWindowTitle("Create new profile")
    wizard.setWizardStyle(QtWidgets.QWizard.ModernStyle)
    wizard.show()

    app.exec_()
