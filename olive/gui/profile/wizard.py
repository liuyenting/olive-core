import logging

from PySide2.QtWidgets import QWizard

from olive.gui.profile import IntroPage, ScriptPage, SequencerPage, DevicesPage

__all__ = ["ProfileWizard"]

logger = logging.getLogger(__name__)


class ProfileWizard(QWizard):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Profile Wizard")
        self.setWizardStyle(QWizard.ModernStyle)

        self.setModal(True)

        self.addPage(IntroPage(self))
        self.addPage(ScriptPage(self))
        self.addPage(SequencerPage(self))
        self.addPage(DevicesPage(self))

    def get_configured_profile(self):
        return None
